from datetime import date, timedelta

from app.game_rules.streaks import week_start


def period_start(kind: str, day: date) -> date:
    return day if kind == "daily" else week_start(day)


def period_end(kind: str, start: date) -> date:
    """Первый день после периода (правая граница не включается)."""
    return start + timedelta(days=1 if kind == "daily" else 7)


def clamp_progress(value: int, target: int) -> int:
    return max(0, min(value, target))


def is_complete(progress: int, target: int) -> bool:
    return progress >= target
