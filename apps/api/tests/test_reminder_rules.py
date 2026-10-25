from datetime import datetime

import pytest

from app.game_rules.reminders import choose_reminder, in_window, parse_hhmm


def test_parse_hhmm():
    assert parse_hhmm("00:00") == 0
    assert parse_hhmm("19:30") == 19 * 60 + 30
    for bad in ("7:00", "24:00", "12:60", "ab:cd", "1200", ""):
        with pytest.raises(ValueError):
            parse_hhmm(bad)


def test_window():
    at = lambda h, m: datetime(2026, 10, 20, h, m)  # noqa: E731
    assert in_window(at(19, 0), "19:00")
    assert in_window(at(21, 59), "19:00")
    assert not in_window(at(18, 59), "19:00")
    assert not in_window(at(22, 0), "19:00")


def kwargs(**over):
    base = dict(streak_weeks=0, weekly_goal=3, week_done=0, today_done=False, weekday=0)
    return {**base, **over}


def test_no_reminder_when_goal_reached_or_trained_today():
    assert choose_reminder(**kwargs(week_done=3)) is None
    assert choose_reminder(**kwargs(today_done=True)) is None


def test_plain_workout_reminder():
    assert choose_reminder(**kwargs()) == "workout"
    assert choose_reminder(**kwargs(streak_weeks=4, weekday=0)) == "workout"  # времени вдоволь


def test_streak_risk_when_days_run_out():
    # четверг (3): осталось 4 дня; нужно 3 тренировки — ещё не критично
    assert choose_reminder(**kwargs(streak_weeks=2, weekday=3)) == "workout"
    # пятница (4): осталось 3 дня, нужно 3 — каждый день на счету
    assert choose_reminder(**kwargs(streak_weeks=2, weekday=4)) == "streak_risk"
    # воскресенье, нужна одна тренировка
    assert choose_reminder(**kwargs(streak_weeks=2, weekday=6, week_done=2)) == "streak_risk"


def test_no_streak_risk_without_streak():
    assert choose_reminder(**kwargs(streak_weeks=0, weekday=6, week_done=2)) == "workout"
