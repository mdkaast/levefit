from datetime import date

from app.game_rules import config as rules
from app.game_rules.achievements import earned_codes, progress
from app.game_rules.ranks import level_points_gained, rank_for_level
from app.game_rules.streaks import StreakState, current_streak, resume_after_pause
from app.game_rules.tasks import needed_workouts, visible_daily_kinds, weekly_tasks_visible


def test_rank_boundaries():
    assert rank_for_level(1) == "novice"
    assert rank_for_level(9) == "novice"
    assert rank_for_level(10) == "amateur"
    assert rank_for_level(19) == "amateur"
    assert rank_for_level(20) == "practitioner"
    assert rank_for_level(30) == "athlete"
    assert rank_for_level(40) == "master"
    assert rank_for_level(49) == "master"
    assert rank_for_level(50) == "expert"
    assert rank_for_level(120) == "expert"


def test_ranks_are_ordered_and_start_at_level_one():
    levels = [level for _, level in rules.RANKS]
    assert levels == sorted(levels) and levels[0] == 1


def test_level_points():
    assert level_points_gained(1, 1) == 0
    assert level_points_gained(1, 2) == rules.LEVEL_POINTS_PER_LEVEL
    assert level_points_gained(3, 6) == 3 * rules.LEVEL_POINTS_PER_LEVEL
    assert level_points_gained(5, 4) == 0  # уровень не снижается, очки не отнимаются


def test_needed_workouts():
    assert needed_workouts(3, 0) == 3
    assert needed_workouts(3, 2) == 1
    assert needed_workouts(3, 5) == 0


def test_daily_task_kinds_by_day_type():
    assert visible_daily_kinds("active", 2) == ("main", "minor")
    assert visible_daily_kinds("active", 0) == ("recovery", "minor")  # день отдыха
    assert visible_daily_kinds("paused", 3) == ("recovery",)  # пауза: без нагрузки
    assert visible_daily_kinds("paused", 0) == ("recovery",)
    assert weekly_tasks_visible("active") and not weekly_tasks_visible("paused")


def test_task_templates_are_valid_data():
    codes = [t["code"] for t in rules.TASK_TEMPLATES]
    assert len(codes) == len(set(codes))
    for t in rules.TASK_TEMPLATES:
        assert t["period"] in rules.TASK_PERIODS and t["kind"] in rules.TASK_KINDS
        assert t["metric"] in rules.TASK_METRICS and t["target"] > 0 and t["xp_reward"] > 0
    kinds = {t["kind"] for t in rules.TASK_TEMPLATES if t["period"] == "daily"}
    assert kinds == {"main", "minor", "recovery"}


def test_achievements_by_stats():
    assert earned_codes({}) == set()
    assert earned_codes({"workouts": 1}) == {"first_workout"}
    got = earned_codes({"workouts": 12, "sets": 120, "streak_weeks": 4, "level": 3})
    assert got == {"first_workout", "workouts_10", "sets_100", "streak_4"}
    assert progress({"workouts": 3}, {"metric": "workouts", "target": 10}) == 3
    assert progress({"workouts": 30}, {"metric": "workouts", "target": 10}) == 10


def test_achievement_metrics_exclude_body_weight():
    assert all("weight" not in a["metric"] for a in rules.ACHIEVEMENTS)


def test_pause_does_not_burn_streak():
    monday = date(2026, 10, 19)
    state = StreakState(weeks=5, freezes_left=1, last_week=monday, freeze_month=date(2026, 10, 1))
    # пауза с 25 октября, возврат через 6 недель — серия сохраняется
    resumed = resume_after_pause(state, date(2026, 10, 25), date(2026, 12, 6))
    assert current_streak(resumed, date(2026, 12, 6)) == 5
    # без сдвига серия сгорела бы
    assert current_streak(state, date(2026, 12, 6)) == 0


def test_resume_without_streak_is_noop():
    empty = StreakState()
    assert resume_after_pause(empty, date(2026, 10, 1), date(2026, 11, 1)) == empty
