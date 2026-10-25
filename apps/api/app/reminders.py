"""Внутренний API для бота: кому прямо сейчас нужно отправить напоминание."""

import hmac
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.game import get_streak_state, utcnow
from app.game_rules import config as rules
from app.game_rules.reminders import choose_reminder, in_window
from app.game_rules.streaks import current_streak, week_start
from app.models import Character, User, XpEvent

router = APIRouter(prefix="/internal")


class DueReminder(BaseModel):
    telegram_id: int
    kind: str  # workout | streak_risk
    streak_weeks: int
    needed: int  # сколько тренировок осталось до недельной цели


def require_internal_key(x_internal_key: str = Header(default="")) -> None:
    key = settings.internal_api_key
    if not key or not hmac.compare_digest(x_internal_key, key):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid internal key")


def _workouts_between(db: Session, user_id: int, start: datetime, end: datetime) -> int:
    return db.scalar(
        select(func.count(XpEvent.id)).where(
            XpEvent.user_id == user_id,
            XpEvent.source == rules.SRC_WORKOUT,
            XpEvent.created_at >= start,
            XpEvent.created_at < end,
        )
    )


def _local_midnight_utc(day, tz: ZoneInfo) -> datetime:
    return datetime.combine(day, time.min, tzinfo=tz).astimezone(UTC)


def collect_due(db: Session, now: datetime) -> list[DueReminder]:
    """Находит пользователей, которым пора отправить напоминание, и помечает их как уведомлённых.

    Отметка ставится сразу (доставка «не более одного раза»): повторно в тот же день
    напоминание не уйдёт, даже если бот не смог его отправить.
    """
    users = db.scalars(
        select(User).join(Character, Character.user_id == User.id).where(User.reminders_enabled)
    ).all()
    due = []
    for user in users:
        tz = ZoneInfo(user.timezone or "UTC")
        local = now.astimezone(tz)
        today = local.date()
        if user.last_reminder_date == today or not in_window(local, user.reminder_time):
            continue

        day_start = _local_midnight_utc(today, tz)
        day_end = _local_midnight_utc(today + timedelta(days=1), tz)
        today_done = _workouts_between(db, user.id, day_start, day_end) > 0
        monday = week_start(today)
        week_start_utc = _local_midnight_utc(monday, tz)
        week_end_utc = _local_midnight_utc(monday + timedelta(7), tz)
        week_done = _workouts_between(db, user.id, week_start_utc, week_end_utc)
        _, state = get_streak_state(db, user.id)
        streak_weeks = current_streak(state, today)
        goal = user.character.workouts_per_week
        kind = choose_reminder(
            streak_weeks=streak_weeks,
            weekly_goal=goal,
            week_done=week_done,
            today_done=today_done,
            weekday=today.weekday(),
        )
        if kind is None:
            continue
        user.last_reminder_date = today
        due.append(
            DueReminder(
                telegram_id=user.telegram_id,
                kind=kind,
                streak_weeks=streak_weeks,
                needed=goal - week_done,
            )
        )
    db.commit()
    return due


@router.post(
    "/reminders/due",
    response_model=list[DueReminder],
    dependencies=[Depends(require_internal_key)],
)
def reminders_due(db: Session = Depends(get_db)) -> list[DueReminder]:
    return collect_due(db, utcnow())
