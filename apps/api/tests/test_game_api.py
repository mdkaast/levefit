from datetime import timedelta

from sqlalchemy import select

from app.game import grant, recompute_character_xp
from app.models import Character, User, XpEvent


def make_character(client, headers, per_week=3):
    body = {"name": "Бодрый", "appearance": "warrior", "workouts_per_week": per_week}
    assert client.post("/characters", json=body, headers=headers).status_code == 201


def do_workout(client, headers, exercise_id, sets=3, **set_fields):
    wid = client.post("/workouts", json={}, headers=headers).json()["id"]
    for _ in range(sets):
        fields = set_fields or {"weight_kg": 80, "reps": 8}
        response = client.post(
            f"/workouts/{wid}/sets", json={"exercise_id": exercise_id, **fields}, headers=headers
        )
        assert response.status_code == 201
    response = client.post(f"/workouts/{wid}/finish", headers=headers)
    assert response.status_code == 200
    return response.json()["reward"]


def test_finish_awards_xp_by_rules(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    reward = do_workout(client, headers, exercises["strength"], sets=3)
    assert reward["counted"] is True
    assert reward["workout_xp"] == 50
    assert reward["sets_xp"] == 15
    assert reward["task_xp"] == 20  # основное задание дня «тренировка»
    assert reward["tasks_completed"] == ["daily_workout"]
    assert reward["xp_gained"] == 85

    character = client.get("/me", headers=headers).json()["character"]
    assert (character["xp"], character["level"]) == (85, 1)
    assert character["xp_in_level"] == 85 and character["xp_to_next"] == 100
    assert character["strength"] == 3 and character["discipline"] == 1


def test_level_up_and_journal_recompute(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    do_workout(client, headers, exercises["strength"], sets=3)
    reward = do_workout(client, headers, exercises["strength"], sets=3)
    assert reward["leveled_up"] is True and reward["level_after"] == 2

    with client.session_factory() as session:
        user = session.scalar(select(User))
        character = session.get(Character, user.id)
        total = character.xp
        character.xp, character.level = 0, 1  # «ломаем» значения
        recompute_character_xp(session, user)
        assert (character.xp, character.level) == (total, 2)
        assert total == sum(session.scalars(select(XpEvent.amount)))


def test_third_workout_per_day_is_not_counted(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers)
    for _ in range(2):
        assert do_workout(client, headers, exercises["strength"])["counted"] is True
    third = do_workout(client, headers, exercises["strength"])
    assert third["counted"] is False and third["xp_gained"] == 0
    assert client.get("/me", headers=headers).json()["character"]["discipline"] == 2


def test_new_day_resets_daily_limit(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers)
    for _ in range(2):
        do_workout(client, headers, exercises["strength"])
    clock.now += timedelta(days=1)
    assert do_workout(client, headers, exercises["strength"])["counted"] is True


def test_sets_xp_is_capped_at_30_sets(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers)
    reward = do_workout(client, headers, exercises["strength"], sets=35, reps=5)
    assert reward["sets_xp"] == 30 * 5


def test_stats_by_category(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers)
    do_workout(client, headers, exercises["cardio"], sets=2, duration_s=600)
    character = client.get("/me", headers=headers).json()["character"]
    assert character["endurance"] == 2 and character["strength"] == 0


def test_grant_is_idempotent(client, auth_headers, clock):
    auth_headers()
    with client.session_factory() as session:
        user = session.scalar(select(User))
        assert grant(session, user.id, "workout", 50, 1, clock.now) == 50
        assert grant(session, user.id, "workout", 50, 1, clock.now) == 0
        assert len(list(session.scalars(select(XpEvent)))) == 1


def test_weekly_goal_extends_streak_and_freeze_saves_it(
    client, auth_headers, exercises, tasks_seeded, clock
):
    headers = auth_headers()
    make_character(client, headers, per_week=1)

    first = do_workout(client, headers, exercises["strength"])
    assert first["week_closed"] is True and first["week_xp"] == 50
    assert first["streak_weeks"] == 1

    clock.now += timedelta(days=7)  # следующая неделя: вторая закрывается
    assert do_workout(client, headers, exercises["strength"])["streak_weeks"] == 2

    clock.now += timedelta(days=14)  # одна неделя пропущена, заморозка спасает серию
    third = do_workout(client, headers, exercises["strength"])
    assert third["streak_weeks"] == 3
    streak = client.get("/me", headers=headers).json()["streak"]
    assert streak["weeks"] == 3 and streak["freezes_left"] == 0


def test_streak_breaks_after_long_gap(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers, per_week=1)
    do_workout(client, headers, exercises["strength"])
    clock.now += timedelta(days=28)
    assert client.get("/me", headers=headers).json()["streak"]["weeks"] == 0
    assert do_workout(client, headers, exercises["strength"])["streak_weeks"] == 1


def test_week_goal_is_paid_once_per_week(client, auth_headers, exercises, clock):
    headers = auth_headers()
    make_character(client, headers, per_week=1)
    do_workout(client, headers, exercises["strength"])
    second = do_workout(client, headers, exercises["strength"])
    assert second["week_closed"] is False and second["week_xp"] == 0


def test_tasks_progress(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers)
    do_workout(client, headers, exercises["strength"], sets=4)
    tasks = {t["code"]: t for t in client.get("/tasks", headers=headers).json()}
    assert tasks["daily_workout"]["status"] == "completed"
    assert tasks["daily_workout"]["kind"] == "main" and tasks["daily_workout"]["period"] == "daily"
    assert tasks["daily_weight"]["kind"] == "minor" and tasks["daily_weight"]["status"] == "active"
    assert "daily_recovery" not in tasks  # в тренировочный день восстановления нет
    assert tasks["weekly_workouts_3"]["progress"] == 1
    assert tasks["weekly_workouts_3"]["target"] == 3
    assert tasks["weekly_sets_40"]["progress"] == 4


def test_weekly_task_pays_once(client, auth_headers, exercises, tasks_seeded, clock):
    headers = auth_headers()
    make_character(client, headers, per_week=7)
    for day in range(3):
        clock.now = clock.now.replace(day=20 + day)  # вт, ср, чт той же недели
        reward = do_workout(client, headers, exercises["strength"], sets=1)
    assert "weekly_workouts_3" in reward["tasks_completed"]
    assert reward["task_xp"] == 100 + 20  # недельное + дневное «тренировка»
    tasks = {t["code"]: t for t in client.get("/tasks", headers=headers).json()}
    assert tasks["weekly_workouts_3"]["status"] == "completed"


def test_user_without_character_gets_nothing(client, auth_headers, exercises, clock):
    headers = auth_headers()
    reward = do_workout(client, headers, exercises["strength"])
    assert reward["counted"] is False and reward["xp_gained"] == 0
