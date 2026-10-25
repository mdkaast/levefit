"""Начисление наград. Решения принимают чистые функции из game_rules; здесь — только работа с БД."""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.game_rules import config as rules
from app.game_rules.levels import level_from_total_xp
from app.game_rules.quests import clamp_progress, is_complete, period_end, period_start
from app.game_rules.rewards import sets_xp, stat_gains, workout_is_counted
from app.game_rules.streaks import StreakState, advance_streak, current_streak, week_start
from app.models import Character, Exercise, Quest, Streak, User, UserQuest, Workout, XpEvent


def utcnow() -> datetime:
    return datetime.now(UTC)


def _bounds(start: date, end: date) -> tuple[datetime, datetime]:
    return (
        datetime(start.year, start.month, start.day, tzinfo=UTC),
        datetime(end.year, end.month, end.day, tzinfo=UTC),
    )


@dataclass
class Reward:
    counted: bool = False
    workout_xp: int = 0
    sets_xp: int = 0
    quest_xp: int = 0
    week_xp: int = 0
    level_before: int = 1
    level_after: int = 1
    quests_completed: list[str] = field(default_factory=list)
    week_closed: bool = False
    streak_weeks: int = 0

    @property
    def xp_gained(self) -> int:
        return self.workout_xp + self.sets_xp + self.quest_xp + self.week_xp


def grant(db: Session, user_id: int, source: str, amount: int, ref_id: int, now: datetime) -> int:
    """Идемпотентное начисление: на (пользователь, источник, основание) только одна запись."""
    if amount <= 0:
        return 0
    exists = db.scalar(
        select(XpEvent.id).where(
            XpEvent.user_id == user_id, XpEvent.source == source, XpEvent.ref_id == ref_id
        )
    )
    if exists:
        return 0
    db.add(XpEvent(user_id=user_id, source=source, amount=amount, ref_id=ref_id, created_at=now))
    db.flush()
    return amount


def _journal(
    db: Session, user_id: int, source: str, start: date, end: date
) -> tuple[int, int]:
    """(число записей, сумма XP) по источнику за [start, end)."""
    lo, hi = _bounds(start, end)
    count, total = db.execute(
        select(func.count(XpEvent.id), func.coalesce(func.sum(XpEvent.amount), 0)).where(
            XpEvent.user_id == user_id,
            XpEvent.source == source,
            XpEvent.created_at >= lo,
            XpEvent.created_at < hi,
        )
    ).one()
    return count, total


def metric_value(db: Session, user_id: int, metric: str, start: date, end: date) -> int:
    if metric == "workouts_finished":
        return _journal(db, user_id, rules.SRC_WORKOUT, start, end)[0]
    if metric == "sets_logged":
        return _journal(db, user_id, rules.SRC_SETS, start, end)[1] // rules.XP_PER_SET
    raise ValueError(f"unknown quest metric: {metric}")


def ensure_user_quests(db: Session, user_id: int, today: date) -> list[UserQuest]:
    """Квесты текущих суток и недели; создаются лениво, прогресс берётся из журнала."""
    result = []
    for quest in db.scalars(select(Quest).order_by(Quest.id)):
        start = period_start(quest.kind, today)
        user_quest = db.scalar(
            select(UserQuest).where(
                UserQuest.user_id == user_id,
                UserQuest.quest_id == quest.id,
                UserQuest.period_start == start,
            )
        )
        if user_quest is None:
            user_quest = UserQuest(
                user_id=user_id, quest_id=quest.id, period_start=start, progress=0, status="active"
            )
            db.add(user_quest)
        if user_quest.status == "active":
            value = metric_value(
                db, user_id, quest.condition["metric"], start, period_end(quest.kind, start)
            )
            user_quest.progress = clamp_progress(value, quest.condition["target"])
        result.append(user_quest)
    db.flush()
    return result


def get_streak_state(db: Session, user_id: int) -> tuple[Streak | None, StreakState]:
    row = db.get(Streak, user_id)
    if row is None:
        return None, StreakState()
    return row, StreakState(row.weeks, row.freezes_left, row.last_week, row.freeze_month)


def streak_view(db: Session, user: User, today: date) -> dict:
    _, state = get_streak_state(db, user.id)
    start = week_start(today)
    return {
        "weeks": current_streak(state, today),
        "freezes_left": state.freezes_left,
        "week_workouts": _journal(db, user.id, rules.SRC_WORKOUT, start, start + timedelta(7))[0],
        "weekly_goal": user.character.workouts_per_week if user.character else 0,
    }


def award_workout(db: Session, user: User, workout: Workout, now: datetime) -> Reward:
    """Единственное место, где начисляется XP за тренировку (вызывается из finish)."""
    character: Character | None = user.character
    if character is None:
        return Reward()
    reward = Reward(level_before=character.level, level_after=character.level)
    today = now.date()

    counted_today = _journal(db, user.id, rules.SRC_WORKOUT, today, today + timedelta(1))[0]
    if not workout_is_counted(counted_today):
        return reward
    reward.counted = True

    reward.workout_xp = grant(db, user.id, rules.SRC_WORKOUT, rules.XP_WORKOUT, workout.id, now)
    if reward.workout_xp == 0:  # уже начислено ранее
        reward.counted = False
        return reward
    reward.sets_xp = grant(
        db, user.id, rules.SRC_SETS, sets_xp(len(workout.sets)), workout.id, now
    )

    category_by_id = dict(
        db.execute(
            select(Exercise.id, Exercise.category).where(
                Exercise.id.in_({s.exercise_id for s in workout.sets})
            )
        ).all()
    )
    for stat, value in stat_gains(category_by_id[s.exercise_id] for s in workout.sets).items():
        setattr(character, stat, getattr(character, stat) + value)
    character.discipline += rules.DISCIPLINE_PER_WORKOUT

    for user_quest in ensure_user_quests(db, user.id, today):
        quest = user_quest.quest
        if user_quest.status == "active" and is_complete(
            user_quest.progress, quest.condition["target"]
        ):
            user_quest.status = "completed"
            source = rules.SRC_QUEST_DAILY if quest.kind == "daily" else rules.SRC_QUEST_WEEKLY
            gained = grant(db, user.id, source, quest.xp_reward, user_quest.id, now)
            reward.quest_xp += gained
            reward.quests_completed.append(quest.code)

    week = week_start(today)
    week_workouts = _journal(db, user.id, rules.SRC_WORKOUT, week, week + timedelta(7))[0]
    row, state = get_streak_state(db, user.id)
    if week_workouts >= character.workouts_per_week:
        gained = grant(db, user.id, rules.SRC_WEEK_GOAL, rules.XP_WEEK_GOAL, week.toordinal(), now)
        if gained:
            reward.week_xp = gained
            reward.week_closed = True
            character.discipline += rules.DISCIPLINE_PER_WEEK_CLOSED
            state = advance_streak(state, week, today)
            if row is None:
                row = Streak(user_id=user.id)
                db.add(row)
            row.weeks, row.freezes_left = state.weeks, state.freezes_left
            row.last_week, row.freeze_month = state.last_week, state.freeze_month
    reward.streak_weeks = current_streak(state, today)

    character.xp += reward.xp_gained
    character.level = level_from_total_xp(character.xp)[0]
    reward.level_after = character.level
    return reward


def recompute_character_xp(db: Session, user: User) -> None:
    """Пересчитывает XP и уровень персонажа из журнала."""
    total = db.scalar(
        select(func.coalesce(func.sum(XpEvent.amount), 0)).where(XpEvent.user_id == user.id)
    )
    if user.character:
        user.character.xp = total
        user.character.level = level_from_total_xp(total)[0]


def award_weight(db: Session, user: User, day: date, now: datetime) -> int:
    """XP за запись веса: один раз в сутки и только за сегодняшнюю дату."""
    character = user.character
    if character is None or day != now.date():
        return 0
    gained = grant(db, user.id, rules.SRC_WEIGHT, rules.XP_WEIGHT_ENTRY, day.toordinal(), now)
    if gained:
        character.xp += gained
        character.level = level_from_total_xp(character.xp)[0]
    return gained
