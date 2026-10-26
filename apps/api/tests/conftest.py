import hashlib
import hmac
import json
import time
from datetime import UTC, datetime
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.adjust import llm_dependency
from app.config import settings
from app.db import Base, get_db
from app.game_rules import config as rules
from app.main import app
from app.models import Exercise, Task

BOT_TOKEN = "123456:TEST-TOKEN"


def make_init_data(
    user: dict | None = None,
    bot_token: str = BOT_TOKEN,
    auth_date: int | None = None,
) -> str:
    fields = {
        "auth_date": str(int(time.time()) if auth_date is None else auth_date),
        "query_id": "AAH",
        "user": json.dumps(user or {"id": 1001, "username": "tester", "language_code": "ru"}),
    }
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setattr(settings, "bot_token", BOT_TOKEN)
    monkeypatch.setattr(settings, "app_secret", "test-secret")
    monkeypatch.setattr(settings, "internal_api_key", "internal-key")


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)

    def override_db():
        with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    test_client = TestClient(app)
    test_client.session_factory = factory
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    def _login(user: dict | None = None) -> dict:
        response = client.post("/auth/telegram", json={"init_data": make_init_data(user)})
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _login


@pytest.fixture
def exercises(client):
    """Общие упражнения: в тестах без миграции справочник создаём сами."""
    with client.session_factory() as session:
        items = [
            Exercise(name="Жим лёжа", category="strength", muscle_group="chest"),
            Exercise(name="Бег", category="cardio", muscle_group="full_body"),
            Exercise(name="Кошка-корова", category="mobility", muscle_group="back"),
        ]
        session.add_all(items)
        session.commit()
        return {e.category: e.id for e in items}


@pytest.fixture
def tasks_seeded(client):
    with client.session_factory() as session:
        for q in rules.TASK_TEMPLATES:
            session.add(
                Task(
                    code=q["code"],
                    period=q["period"],
                    kind=q["kind"],
                    condition={"metric": q["metric"], "target": q["target"]},
                    xp_reward=q["xp_reward"],
                )
            )
        session.commit()


@pytest.fixture
def clock(monkeypatch):
    """Управляемое «сейчас» для игровой логики; clock.now можно менять."""

    class Clock:
        now = datetime(2026, 10, 20, 12, tzinfo=UTC)  # вторник

    monkeypatch.setattr("app.game.utcnow", lambda: Clock.now)
    monkeypatch.setattr("app.routers.utcnow", lambda: Clock.now)
    monkeypatch.setattr("app.workouts.utcnow", lambda: Clock.now)
    monkeypatch.setattr("app.metrics.utcnow", lambda: Clock.now)
    monkeypatch.setattr("app.reminders.utcnow", lambda: Clock.now)
    monkeypatch.setattr("app.tasks_routes.utcnow", lambda: Clock.now)
    return Clock


@pytest.fixture
def use_llm(client):
    """Подставляет ИИ-тренера (или None) вместо настоящего провайдера."""

    def _use(llm):
        app.dependency_overrides[llm_dependency] = lambda: llm
        return llm

    yield _use
    app.dependency_overrides.pop(llm_dependency, None)
