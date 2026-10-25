from datetime import datetime

from app.game_rules import config as rules


def parse_hhmm(value: str) -> int:
    """'19:30' -> минуты от начала суток; ValueError при неверном формате."""
    if len(value) != 5 or value[2] != ":" or not (value[:2] + value[3:]).isdigit():
        raise ValueError("expected HH:MM")
    hours, minutes = int(value[:2]), int(value[3:])
    if hours > 23 or minutes > 59:
        raise ValueError("expected HH:MM")
    return hours * 60 + minutes


def in_window(local_now: datetime, reminder_time: str) -> bool:
    """Пора ли слать: заданное время наступило, и с него прошло меньше окна."""
    passed = local_now.hour * 60 + local_now.minute - parse_hhmm(reminder_time)
    return 0 <= passed < rules.REMINDER_WINDOW_MIN


def choose_reminder(
    *,
    streak_weeks: int,
    weekly_goal: int,
    week_done: int,
    today_done: bool,
    weekday: int,
) -> str | None:
    """Какое напоминание отправить: 'streak_risk', 'workout' или None.

    Напоминаем только пока недельная цель не достигнута и сегодня ещё не тренировались:
    дни отдыха нужны, поэтому в остальные дни бот молчит.
    """
    needed = weekly_goal - week_done
    if needed <= 0 or today_done:
        return None
    days_left = 7 - weekday  # включая сегодня; понедельник = 0
    if streak_weeks > 0 and days_left <= needed:
        return "streak_risk"
    return "workout"
