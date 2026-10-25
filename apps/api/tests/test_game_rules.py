from datetime import date

from app.game_rules import config as rules
from app.game_rules.levels import level_from_total_xp, xp_for_next_level
from app.game_rules.quests import clamp_progress, is_complete, period_end, period_start
from app.game_rules.rewards import counted_sets, sets_xp, stat_gains, workout_is_counted
from app.game_rules.streaks import (
    StreakState,
    advance_streak,
    current_streak,
    refill_freezes,
    week_start,
)


def test_level_thresholds():
    assert xp_for_next_level(1) == 100
    assert xp_for_next_level(3) == 300
    assert level_from_total_xp(0) == (1, 0)
    assert level_from_total_xp(99) == (1, 99)
    assert level_from_total_xp(100) == (2, 0)
    assert level_from_total_xp(299) == (2, 199)
    assert level_from_total_xp(300) == (3, 0)  # 100 + 200
    assert level_from_total_xp(600) == (4, 0)  # 100 + 200 + 300
    assert level_from_total_xp(-5) == (1, 0)


def test_workout_daily_limit():
    assert workout_is_counted(0) and workout_is_counted(1)
    assert not workout_is_counted(2)


def test_sets_are_capped():
    assert counted_sets(10) == 10
    assert counted_sets(100) == rules.MAX_COUNTED_SETS_PER_WORKOUT
    assert sets_xp(3) == 15
    assert sets_xp(100) == 30 * rules.XP_PER_SET
    assert sets_xp(0) == 0


def test_stat_gains_by_category():
    gains = stat_gains(["strength", "strength", "cardio", "mobility", "unknown"])
    assert gains == {"strength": 2, "endurance": 1, "agility": 1}


def test_stat_gains_ignore_sets_over_cap():
    assert stat_gains(["strength"] * 50) == {"strength": rules.MAX_COUNTED_SETS_PER_WORKOUT}


MON = date(2026, 10, 19)


def test_week_start_is_monday():
    assert week_start(date(2026, 10, 25)) == MON  # воскресенье
    assert week_start(MON) == MON


def test_first_week_starts_streak():
    state = advance_streak(StreakState(), MON, MON)
    assert (state.weeks, state.last_week) == (1, MON)


def test_consecutive_weeks_extend_streak():
    state = advance_streak(StreakState(), date(2026, 10, 12), date(2026, 10, 12))
    state = advance_streak(state, MON, MON)
    assert state.weeks == 2


def test_same_week_is_idempotent():
    once = advance_streak(StreakState(), MON, MON)
    assert advance_streak(once, MON, MON) == once


def test_freeze_saves_streak_after_missed_week():
    state = StreakState(
        weeks=4, freezes_left=1, last_week=date(2026, 10, 5), freeze_month=date(2026, 10, 1)
    )
    state = advance_streak(state, MON, MON)  # пропущена неделя 12 октября
    assert state.weeks == 5 and state.freezes_left == 0


def test_streak_resets_without_freeze_or_after_long_gap():
    no_freeze = StreakState(
        weeks=4, freezes_left=0, last_week=date(2026, 10, 5), freeze_month=date(2026, 10, 1)
    )
    assert advance_streak(no_freeze, MON, MON).weeks == 1
    long_gap = StreakState(
        weeks=4, freezes_left=1, last_week=date(2026, 9, 21), freeze_month=date(2026, 10, 1)
    )
    assert advance_streak(long_gap, MON, MON).weeks == 1


def test_freezes_refill_each_month():
    spent = StreakState(freezes_left=0, freeze_month=date(2026, 9, 1))
    assert refill_freezes(spent, date(2026, 10, 3)).freezes_left == rules.FREEZES_PER_MONTH
    same_month = StreakState(freezes_left=0, freeze_month=date(2026, 10, 1))
    assert refill_freezes(same_month, date(2026, 10, 20)).freezes_left == 0


def test_current_streak_display():
    state = StreakState(weeks=3, freezes_left=1, last_week=MON, freeze_month=date(2026, 10, 1))
    assert current_streak(state, date(2026, 10, 25)) == 3  # неделя закрыта
    assert current_streak(state, date(2026, 10, 28)) == 3  # новая неделя в процессе
    assert current_streak(state, date(2026, 11, 4)) == 3  # пропуск, но есть заморозка
    spent = StreakState(weeks=3, freezes_left=0, last_week=MON, freeze_month=date(2026, 11, 1))
    assert current_streak(spent, date(2026, 11, 4)) == 0
    assert current_streak(StreakState(), MON) == 0


def test_quest_periods():
    assert period_start("daily", date(2026, 10, 22)) == date(2026, 10, 22)
    assert period_start("weekly", date(2026, 10, 22)) == MON
    assert period_end("daily", date(2026, 10, 22)) == date(2026, 10, 23)
    assert period_end("weekly", MON) == date(2026, 10, 26)


def test_quest_progress():
    assert clamp_progress(5, 3) == 3
    assert clamp_progress(-1, 3) == 0
    assert is_complete(3, 3) and not is_complete(2, 3)


def test_quest_templates_are_valid_data():
    codes = [q["code"] for q in rules.QUEST_TEMPLATES]
    assert len(codes) == len(set(codes))
    for q in rules.QUEST_TEMPLATES:
        assert q["kind"] in ("daily", "weekly")
        assert q["metric"] in rules.QUEST_METRICS
        assert q["target"] > 0
