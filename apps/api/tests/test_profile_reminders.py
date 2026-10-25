from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from app.models import (
    BodyMetric,
    Character,
    Exercise,
    Streak,
    User,
    UserAchievement,
    UserTask,
    Workout,
    WorkoutSet,
    XpEvent,
)

INTERNAL = {"X-Internal-Key": "internal-key"}


def make_character(client, headers, per_week=3):
    body = {"name": "Бодрый", "appearance": "warrior", "workouts_per_week": per_week}
    assert client.post("/characters", json=body, headers=headers).status_code == 201


def due(client):
    response = client.post("/internal/reminders/due", headers=INTERNAL)
    assert response.status_code == 200
    return response.json()


def do_workout(client, headers, exercise_id):
    wid = client.post("/workouts", json={}, headers=headers).json()["id"]
    client.post(
        f"/workouts/{wid}/sets", json={"exercise_id": exercise_id, "reps": 5}, headers=headers
    )
    assert client.post(f"/workouts/{wid}/finish", headers=headers).status_code == 200


# ---------- настройки профиля ----------


def test_defaults_and_patch(client, auth_headers):
    headers = auth_headers()
    user = client.get("/me", headers=headers).json()["user"]
    assert user["reminders_enabled"] is True
    assert user["reminder_time"] == "19:00" and user["timezone"] is None

    patched = client.patch(
        "/me",
        json={"reminders_enabled": False, "reminder_time": "07:30", "timezone": "Europe/Moscow"},
        headers=headers,
    )
    assert patched.status_code == 200
    assert patched.json()["reminder_time"] == "07:30"
    assert patched.json()["timezone"] == "Europe/Moscow"
    assert patched.json()["reminders_enabled"] is False

    only_flag = client.patch("/me", json={"reminders_enabled": True}, headers=headers).json()
    assert only_flag["reminder_time"] == "07:30"  # остальное не тронуто


def test_patch_validation(client, auth_headers):
    headers = auth_headers()
    for bad in (
        {"reminder_time": "25:00"},
        {"reminder_time": "7:00"},
        {"timezone": "Mars/Base"},
        {"reminders_enabled": "maybe"},
    ):
        assert client.patch("/me", json=bad, headers=headers).status_code == 422


def test_patch_requires_auth(client):
    assert client.patch("/me", json={}).status_code == 401
    assert client.delete("/me").status_code == 401


# ---------- удаление аккаунта ----------


def test_delete_me_removes_everything(client, auth_headers, exercises, tasks_seeded, clock):
    a = auth_headers({"id": 1, "username": "a"})
    b = auth_headers({"id": 2, "username": "b"})
    for headers in (a, b):
        make_character(client, headers, per_week=1)
        do_workout(client, headers, exercises["strength"])
        client.put("/metrics/weight", json={"weight_kg": 80}, headers=headers)
        client.get("/tasks", headers=headers)
    client.post(
        "/exercises",
        json={"name": "Моё", "category": "strength", "muscle_group": "arms"},
        headers=a,
    )

    assert client.delete("/me", headers=a).status_code == 204
    assert client.get("/me", headers=a).status_code == 401  # токен больше не действует

    with client.session_factory() as session:
        user_a = session.scalar(select(User).where(User.telegram_id == 1))
        assert user_a is None
        remaining_users = {u.telegram_id for u in session.scalars(select(User))}
        assert remaining_users == {2}
        uid = session.scalar(select(User.id))
        for model, column in (
            (Character, Character.user_id),
            (Workout, Workout.user_id),
            (XpEvent, XpEvent.user_id),
            (UserTask, UserTask.user_id),
            (UserAchievement, UserAchievement.user_id),
            (BodyMetric, BodyMetric.user_id),
            (Streak, Streak.user_id),
        ):
            others = session.scalar(
                select(func.count()).select_from(model).where(column != uid)
            )
            assert others == 0, model.__name__
        assert session.scalar(select(func.count()).select_from(WorkoutSet)) == 1
        owned = session.scalar(
            select(func.count()).select_from(Exercise).where(Exercise.owner_id.is_not(None))
        )
        assert owned == 0


# ---------- внутренний эндпоинт напоминаний ----------


def test_internal_endpoint_requires_key(client):
    assert client.post("/internal/reminders/due").status_code == 401
    wrong = client.post("/internal/reminders/due", headers={"X-Internal-Key": "nope"})
    assert wrong.status_code == 401


def test_internal_endpoint_disabled_without_configured_key(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "internal_api_key", "")
    assert client.post("/internal/reminders/due", headers={"X-Internal-Key": ""}).status_code == 401


def test_reminder_sent_at_set_time_once_per_day(client, auth_headers, clock):
    headers = auth_headers({"id": 77, "username": "r"})
    make_character(client, headers)
    client.patch("/me", json={"reminder_time": "19:00", "timezone": "UTC"}, headers=headers)

    clock.now = datetime(2026, 10, 20, 18, 59, tzinfo=UTC)
    assert due(client) == []  # рано

    clock.now = datetime(2026, 10, 20, 19, 0, tzinfo=UTC)
    first = due(client)
    assert len(first) == 1
    assert {k: first[0][k] for k in ("telegram_id", "kind", "streak_weeks", "needed")} == {
        "telegram_id": 77, "kind": "workout", "streak_weeks": 0, "needed": 3,
    }
    assert first[0]["reward_xp"] == 50 and first[0]["days_left"] == 6  # вторник
    assert due(client) == []  # повторно в тот же день не шлём

    clock.now = datetime(2026, 10, 21, 19, 5, tzinfo=UTC)
    assert len(due(client)) == 1  # на следующий день снова


def test_reminder_respects_timezone(client, auth_headers, clock):
    headers = auth_headers({"id": 78, "username": "tz"})
    make_character(client, headers)
    client.patch(
        "/me", json={"reminder_time": "20:00", "timezone": "Asia/Yekaterinburg"}, headers=headers
    )  # UTC+5
    clock.now = datetime(2026, 10, 20, 15, 0, tzinfo=UTC)  # 20:00 по местному
    assert len(due(client)) == 1


def test_reminder_not_sent_after_window(client, auth_headers, clock):
    headers = auth_headers()
    make_character(client, headers)
    client.patch("/me", json={"reminder_time": "10:00", "timezone": "UTC"}, headers=headers)
    clock.now = datetime(2026, 10, 20, 14, 0, tzinfo=UTC)  # позже окна в 3 часа
    assert due(client) == []


def test_disabled_and_characterless_users_get_nothing(client, auth_headers, clock):
    off = auth_headers({"id": 1, "username": "off"})
    make_character(client, off)
    off_settings = {"reminders_enabled": False, "reminder_time": "19:00", "timezone": "UTC"}
    client.patch("/me", json=off_settings, headers=off)
    auth_headers({"id": 2, "username": "nochar"})  # без персонажа
    clock.now = datetime(2026, 10, 20, 19, 30, tzinfo=UTC)
    assert due(client) == []


def test_no_reminder_if_trained_today_or_goal_reached(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers, per_week=3)
    client.patch("/me", json={"reminder_time": "19:00", "timezone": "UTC"}, headers=headers)
    do_workout(client, headers, exercises["strength"])  # сегодня уже тренировались
    clock.now = datetime(2026, 10, 20, 19, 0, tzinfo=UTC)
    assert due(client) == []


def test_streak_risk_reminder(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers, per_week=1)
    client.patch("/me", json={"reminder_time": "19:00", "timezone": "UTC"}, headers=headers)
    do_workout(client, headers, exercises["strength"])  # закрыта неделя 19 окт, серия 1

    # следующая неделя: в воскресенье 1 тренировка нужна, день последний
    clock.now = datetime(2026, 10, 25, 19, 0, tzinfo=UTC) + timedelta(days=7)
    result = due(client)
    assert len(result) == 1
    assert (result[0]["kind"], result[0]["streak_weeks"], result[0]["needed"]) == (
        "streak_risk", 1, 1)
    assert result[0]["days_left"] == 1 and result[0]["freezes_left"] == 1
    # в начале той же недели серия жива, но времени достаточно: обычное напоминание
    client.patch("/me", json={"reminder_time": "19:00"}, headers=headers)  # сброс отметки дня
    clock.now = datetime(2026, 10, 26, 19, 0, tzinfo=UTC)  # понедельник новой недели
    assert due(client)[0]["kind"] == "workout"
