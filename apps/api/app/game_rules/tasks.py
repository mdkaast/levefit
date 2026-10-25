from datetime import date, timedelta

from app.game_rules.streaks import week_start


def period_start(period: str, day: date) -> date:
    return day if period == "daily" else week_start(day)


def period_end(period: str, start: date) -> date:
    """Первый день после периода (правая граница не включается)."""
    return start + timedelta(days=1 if period == "daily" else 7)


def clamp_progress(value: int, target: int) -> int:
    return max(0, min(value, target))


def is_complete(progress: int, target: int) -> bool:
    return progress >= target


def needed_workouts(weekly_goal: int, done_before_today: int) -> int:
    """Сколько тренировок недельной цели осталось на начало сегодняшнего дня."""
    return max(0, weekly_goal - done_before_today)


def visible_daily_kinds(mode: str, needed_at_start: int) -> tuple[str, ...]:
    """Какие ежедневные задания выдаются сегодня.

    Пауза (болезнь или травма): только лёгкое восстановление, заданий с нагрузкой нет.
    Пока недельная цель не выполнена — основное и малое. Цель выполнена — день отдыха:
    восстановление и малое. Состав считается на начало дня и не меняется до его конца.
    """
    if mode == "paused":
        return ("recovery",)
    if needed_at_start > 0:
        return ("main", "minor")
    return ("recovery", "minor")


def weekly_tasks_visible(mode: str) -> bool:
    return mode != "paused"
