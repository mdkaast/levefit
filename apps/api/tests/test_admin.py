import pytest

from app.config import settings
from tests.test_ai_adjust import FakeLLM, explanation
from tests.test_coach import ADMIN, adjusted_workout, use_llm  # noqa: F401

OWNER = {"id": 777, "first_name": "Owner"}


@pytest.fixture(autouse=True)
def _admin(monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "admin-key")
    monkeypatch.setattr(settings, "admin_telegram_ids", "777, 12")


def test_admin_access_by_telegram_id_or_key(client, auth_headers):
    owner = auth_headers(OWNER)
    stranger = auth_headers({"id": 5, "first_name": "X"})
    assert client.get("/admin/stats", headers=owner).status_code == 200
    assert client.get("/admin/stats", headers=ADMIN).status_code == 200
    assert client.get("/admin/stats", headers=stranger).status_code == 401
    assert client.get("/admin/stats").status_code == 401
    assert client.get("/admin/stats", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_me_reports_admin_flag(client, auth_headers):
    assert client.get("/me", headers=auth_headers(OWNER)).json()["is_admin"] is True
    assert (
        client.get("/me", headers=auth_headers({"id": 5, "first_name": "X"})).json()["is_admin"]
        is False
    )


def test_coach_rules_open_to_admin_user(client, auth_headers):
    owner = auth_headers(OWNER)
    created = client.post("/admin/coach/rules", json={"text": "Правило владельца"}, headers=owner)
    assert created.status_code == 201


def test_stats_counts(client, auth_headers, exercises, use_llm):  # noqa: F811
    headers = auth_headers(OWNER)
    bench = exercises["strength"]
    use_llm(FakeLLM(explanation()))
    wid = adjusted_workout(client, headers, bench)
    client.post(f"/workouts/{wid}/adjust/feedback", json={"rating": "too_hard"}, headers=headers)
    data = client.get("/admin/stats", headers=ADMIN).json()
    assert data["users"]["total"] == 1 and data["users"]["active_7d"] == 1
    assert data["workouts"]["finished"] == 1 and data["workouts"]["sets"] == 3
    assert len(data["workouts"]["daily"]) == 14
    assert data["ai"]["total"] == 1
    assert data["ai"]["ratings"] == {"fits": 0, "too_hard": 1, "too_easy": 0}
    assert data["ai"]["by_decision"] == [{"decision": "keep_weight", "count": 1}]
    recent = client.get("/admin/ai/recent", headers=ADMIN).json()
    assert recent[0]["rating"] == "too_hard" and recent[0]["decision"] == "keep_weight"
    assert "input_snapshot" not in recent[0]


def test_change_requests_lifecycle(client):
    body = {"title": "Новая кнопка", "prompt": "Добавь кнопку на главный экран"}
    created = client.post("/admin/requests", json=body, headers=ADMIN)
    assert created.status_code == 201 and created.json()["status"] == "draft"
    rid = created.json()["id"]
    assert (
        client.post(
            "/admin/requests", json={"title": "a", "prompt": "b"}, headers=ADMIN
        ).status_code
        == 422
    )
    patched = client.patch(f"/admin/requests/{rid}", json={"status": "sent"}, headers=ADMIN)
    assert patched.json()["status"] == "sent"
    assert (
        client.patch(f"/admin/requests/{rid}", json={"status": "x"}, headers=ADMIN).status_code
        == 422
    )
    assert [r["id"] for r in client.get("/admin/requests", headers=ADMIN).json()] == [rid]
    assert client.delete(f"/admin/requests/{rid}", headers=ADMIN).status_code == 204
    assert client.delete(f"/admin/requests/{rid}", headers=ADMIN).status_code == 404
