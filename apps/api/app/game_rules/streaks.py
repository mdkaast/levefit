from dataclasses import dataclass, replace
from datetime import date, timedelta

from app.game_rules.config import FREEZES_PER_MONTH


@dataclass(frozen=True)
class StreakState:
    weeks: int = 0
    freezes_left: int = FREEZES_PER_MONTH
    last_week: date | None = None
    freeze_month: date | None = None


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def month_start(day: date) -> date:
    return day.replace(day=1)


def refill_freezes(state: StreakState, today: date) -> StreakState:
    """Раз в месяц заморозки восстанавливаются."""
    if state.freeze_month == month_start(today):
        return state
    return replace(state, freezes_left=FREEZES_PER_MONTH, freeze_month=month_start(today))


def advance_streak(state: StreakState, week: date, today: date) -> StreakState:
    """Учитывает закрытую неделю `week` (её понедельник). Повторный вызов ничего не меняет."""
    state = refill_freezes(state, today)
    if state.last_week == week:
        return state
    if state.last_week is None:
        return replace(state, weeks=1, last_week=week)
    gap = (week - state.last_week).days // 7
    if gap == 1:
        return replace(state, weeks=state.weeks + 1, last_week=week)
    if gap == 2 and state.freezes_left > 0:
        return replace(
            state, weeks=state.weeks + 1, freezes_left=state.freezes_left - 1, last_week=week
        )
    return replace(state, weeks=1, last_week=week)


def current_streak(state: StreakState, today: date) -> int:
    """Серия, которую нужно показывать сегодня (0, если она уже прервана)."""
    if state.last_week is None:
        return 0
    gap = (week_start(today) - state.last_week).days // 7
    if gap <= 1:
        return state.weeks
    if gap == 2 and refill_freezes(state, today).freezes_left > 0:
        return state.weeks
    return 0


def resume_after_pause(state: StreakState, paused_on: date, resumed_on: date) -> StreakState:
    """Сдвигает серию на длину паузы в целых неделях, чтобы пауза не считалась пропуском."""
    if state.last_week is None:
        return state
    paused_weeks = max(0, (week_start(resumed_on) - week_start(paused_on)).days // 7)
    return replace(state, last_week=state.last_week + timedelta(weeks=paused_weeks))
