from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.game import apply_xp
from app.game_rules import config as rules
from app.models import Character, Streak, User


def make_character(client, headers, per_week=3):
    body = {"name": "Бодрый", "workouts_per_week": per_week}
    assert client.post("/characters", json=body, headers=headers).status_code == 201


def do_workout(client, headers, exercise_id, sets=3):
    wid = client.post("/workouts", json={}, headers=headers).json()["id"]
    for _ in range(sets):
        client.post(
            f"/workouts/{wid}/sets",
            json={"exercise_id": exercise_id, "weight_kg": 80, "reps": 8},
            headers=headers,
        )
    response = client.post(f"/workouts/{wid}/finish", headers=headers)
    assert response.status_code == 200
    return response.json()["reward"]


def tasks_by_code(client, headers):
    return {t["code"]: t for t in client.get("/tasks", headers=headers).json()}


# ---------- ранги и очки уровня ----------


def test_apply_xp_updates_rank_and_level_points():
    character = Character(level=1, xp=0, level_points=0, rank="novice")
    before, after = apply_xp(character, 4500)  # 100 + 200 + … + 900: уровень 10
    assert (before, after) == (1, 10)
    assert character.rank == "amateur"
    assert character.level_points == 9


def test_new_character_starts_as_novice(client, auth_headers):
    headers = auth_headers()
    make_character(client, headers)
    character = client.get("/me", headers=headers).json()["character"]
    assert character["rank"] == "novice" and character["level_points"] == 0


def test_level_up_gives_level_point(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    do_workout(client, headers, exercises["strength"])
    reward = do_workout(client, headers, exercises["strength"])  # 85 + 65 XP: уровень 2
    assert reward["leveled_up"] is True and reward["level_points_gained"] == 1
    assert reward["rank_changed"] is False
    assert client.get("/me", headers=headers).json()["character"]["level_points"] == 1


def test_xp_is_never_removed(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    do_workout(client, headers, exercises["strength"])
    xp_before = client.get("/me", headers=headers).json()["character"]["xp"]
    clock.now += timedelta(days=30)  # месяц без тренировок
    client.get("/tasks", headers=headers)
    me = client.get("/me", headers=headers).json()["character"]
    assert me["xp"] == xp_before  # пропуск не снимает ни XP, ни уровень, ни характеристики
    assert me["strength"] == 3 and me["level"] == 1


# ---------- виды заданий, день отдыха ----------


def test_training_day_has_main_and_minor_tasks(client, auth_headers, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    tasks = tasks_by_code(client, headers)
    assert {"daily_workout", "daily_weight", "weekly_workouts_3", "weekly_sets_40"} <= set(tasks)
    assert "daily_recovery" not in tasks


def test_rest_day_gives_recovery_instead_of_main(
    client, auth_headers, exercises, tasks_seeded, clock
):
    headers = auth_headers()
    make_character(client, headers, per_week=1)
    do_workout(client, headers, exercises["strength"])  # недельная цель выполнена
    clock.now += timedelta(days=1)
    tasks = tasks_by_code(client, headers)
    assert "daily_workout" not in tasks and "daily_recovery" in tasks
    assert tasks["daily_recovery"]["kind"] == "recovery"
    assert "daily_weight" in tasks  # малое задание остаётся


def test_recovery_task_is_confirmed_once(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers, per_week=1)
    do_workout(client, headers, exercises["strength"])
    clock.now += timedelta(days=1)
    task = tasks_by_code(client, headers)["daily_recovery"]
    xp_before = client.get("/me", headers=headers).json()["character"]["xp"]

    done = client.post(f"/tasks/{task['id']}/complete", headers=headers)
    assert done.status_code == 200 and done.json()["task_xp"] == 10
    assert client.get("/me", headers=headers).json()["character"]["xp"] == xp_before + 10
    again = client.post(f"/tasks/{task['id']}/complete", headers=headers)
    assert again.status_code == 409
    assert tasks_by_code(client, headers)["daily_recovery"]["status"] == "completed"


def test_only_recovery_tasks_are_confirmed_manually(client, auth_headers, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    main = tasks_by_code(client, headers)["daily_workout"]
    assert client.post(f"/tasks/{main['id']}/complete", headers=headers).status_code == 409
    assert client.post("/tasks/99999/complete", headers=headers).status_code == 404


def test_other_users_task_is_hidden(client, auth_headers, exercises, tasks_seeded, clock):
    a = auth_headers({"id": 1, "username": "a"})
    b = auth_headers({"id": 2, "username": "b"})
    make_character(client, a, per_week=1)
    make_character(client, b)
    do_workout(client, a, exercises["strength"])
    clock.now += timedelta(days=1)
    task = tasks_by_code(client, a)["daily_recovery"]
    assert client.post(f"/tasks/{task['id']}/complete", headers=b).status_code == 404


def test_weight_entry_completes_minor_task(client, auth_headers, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    saved = client.put("/metrics/weight", json={"weight_kg": 80}, headers=headers).json()
    assert saved["xp_gained"] == 5 + 10  # запись веса и малое задание дня
    assert tasks_by_code(client, headers)["daily_weight"]["status"] == "completed"


# ---------- режим паузы ----------


def test_pause_gives_only_recovery_tasks(client, auth_headers, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    paused = client.patch("/me", json={"mode": "paused"}, headers=headers)
    assert paused.status_code == 200 and paused.json()["mode"] == "paused"
    assert set(tasks_by_code(client, headers)) == {"daily_recovery"}  # без нагрузки и недельных

    client.patch("/me", json={"mode": "active"}, headers=headers)
    assert "daily_workout" in tasks_by_code(client, headers)


def test_pause_keeps_streak(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers, per_week=1)
    do_workout(client, headers, exercises["strength"])  # серия: 1 неделя
    client.patch("/me", json={"mode": "paused"}, headers=headers)

    clock.now += timedelta(weeks=8)  # долгая пауза
    assert client.get("/me", headers=headers).json()["streak"]["weeks"] == 1  # заморожена

    client.patch("/me", json={"mode": "active"}, headers=headers)
    assert client.get("/me", headers=headers).json()["streak"]["weeks"] == 1
    with client.session_factory() as session:
        assert session.scalar(select(Streak)).weeks == 1


def test_without_pause_long_gap_resets_streak(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers, per_week=1)
    do_workout(client, headers, exercises["strength"])
    clock.now += timedelta(weeks=8)
    assert client.get("/me", headers=headers).json()["streak"]["weeks"] == 0


def test_mode_validation(client, auth_headers):
    headers = auth_headers()
    assert client.patch("/me", json={"mode": "vacation"}, headers=headers).status_code == 422


def test_paused_user_gets_no_reminders(client, auth_headers, clock):
    headers = auth_headers()
    make_character(client, headers)
    client.patch(
        "/me", json={"reminder_time": "19:00", "timezone": "UTC", "mode": "paused"}, headers=headers
    )
    clock.now = datetime(2026, 10, 20, 19, 0, tzinfo=UTC)
    response = client.post("/internal/reminders/due", headers={"X-Internal-Key": "internal-key"})
    assert response.json() == []


def test_user_mode_defaults(client, auth_headers):
    headers = auth_headers()
    assert client.get("/me", headers=headers).json()["user"]["mode"] == "active"
    with client.session_factory() as session:
        assert session.scalar(select(User)).paused_at is None


# ---------- достижения и прочее ----------


def test_achievements_are_awarded_once(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    first = do_workout(client, headers, exercises["strength"])
    assert "first_workout" in first["achievements_earned"]
    second = do_workout(client, headers, exercises["strength"])
    assert second["achievements_earned"] == []

    listing = {a["code"]: a for a in client.get("/achievements", headers=headers).json()}
    assert listing["first_workout"]["earned"] is True and listing["first_workout"]["earned_at"]
    assert listing["workouts_10"]["earned"] is False
    assert (listing["workouts_10"]["progress"], listing["workouts_10"]["target"]) == (2, 10)


def test_task_endpoints_require_auth(client):
    assert client.get("/achievements").status_code == 401
    assert client.get("/tasks").status_code == 401


def test_finish_reports_stat_gains(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers)
    reward = do_workout(client, headers, exercises["strength"], sets=3)
    assert reward["stat_gains"] == {"strength": 3, "discipline": 1}


def test_reminders_limit_per_day_is_configurable(client, auth_headers, clock, monkeypatch):
    monkeypatch.setattr(rules, "MAX_REMINDERS_PER_DAY", 2)
    headers = auth_headers()
    make_character(client, headers)
    client.patch("/me", json={"reminder_time": "19:00", "timezone": "UTC"}, headers=headers)
    clock.now = datetime(2026, 10, 20, 19, 0, tzinfo=UTC)

    def due():
        r = client.post("/internal/reminders/due", headers={"X-Internal-Key": "internal-key"})
        return len(r.json())

    assert (due(), due(), due()) == (1, 1, 0)
