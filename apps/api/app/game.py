"""Начисление наград. Решения принимают чистые функции из game_rules; здесь — только работа с БД."""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.game_rules import config as rules
from app.game_rules.achievements import earned_codes
from app.game_rules.levels import level_from_total_xp
from app.game_rules.ranks import level_points_gained, rank_for_level
from app.game_rules.rewards import sets_xp, stat_gains, workout_is_counted
from app.game_rules.streaks import (
    StreakState,
    advance_streak,
    current_streak,
    resume_after_pause,
    week_start,
)
from app.game_rules.tasks import (
    clamp_progress,
    is_complete,
    needed_workouts,
    period_end,
    period_start,
    visible_daily_kinds,
    weekly_tasks_visible,
)
from app.models import (
    Character,
    Exercise,
    Streak,
    Task,
    User,
    UserAchievement,
    UserTask,
    Workout,
    XpEvent,
)


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
    task_xp: int = 0
    week_xp: int = 0
    weight_xp: int = 0
    level_before: int = 1
    level_after: int = 1
    rank_before: str = "novice"
    rank_after: str = "novice"
    level_points_gained: int = 0
    stat_gains: dict[str, int] = field(default_factory=dict)
    tasks_completed: list[str] = field(default_factory=list)
    achievements_earned: list[str] = field(default_factory=list)
    week_closed: bool = False
    streak_weeks: int = 0

    @property
    def xp_gained(self) -> int:
        return self.workout_xp + self.sets_xp + self.task_xp + self.week_xp + self.weight_xp


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


def apply_xp(character: Character, amount: int) -> tuple[int, int]:
    """Добавляет XP персонажу; пересчитывает уровень, ранг и очки уровня. Возвращает (до, после)."""
    before = character.level
    character.xp += amount
    character.level = level_from_total_xp(character.xp)[0]
    character.level_points += level_points_gained(before, character.level)
    character.rank = rank_for_level(character.level)
    return before, character.level


def _journal(db: Session, user_id: int, source: str, start: date, end: date) -> tuple[int, int]:
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


def _journal_total(db: Session, user_id: int, source: str) -> tuple[int, int]:
    """(число записей, сумма XP) по источнику за всё время."""
    return db.execute(
        select(func.count(XpEvent.id), func.coalesce(func.sum(XpEvent.amount), 0)).where(
            XpEvent.user_id == user_id, XpEvent.source == source
        )
    ).one()


def metric_value(db: Session, user_id: int, metric: str, start: date, end: date) -> int:
    if metric == "workouts_finished":
        return _journal(db, user_id, rules.SRC_WORKOUT, start, end)[0]
    if metric == "sets_logged":
        return _journal(db, user_id, rules.SRC_SETS, start, end)[1] // rules.XP_PER_SET
    if metric == "weight_entries":
        return _journal(db, user_id, rules.SRC_WEIGHT, start, end)[0]
    raise ValueError(f"unknown task metric: {metric}")


def needed_at_start_of_day(db: Session, user: User, today: date) -> int:
    """Сколько тренировок недельной цели осталось на начало сегодняшнего дня."""
    if user.character is None:
        return 0
    done = _journal(db, user.id, rules.SRC_WORKOUT, week_start(today), today)[0]
    return needed_workouts(user.character.workouts_per_week, done)


def visible_tasks(db: Session, user: User, today: date) -> list[Task]:
    """Задания, выдаваемые сегодня: состав зависит от режима и от дня (тренировка или отдых)."""
    daily_kinds = visible_daily_kinds(user.mode, needed_at_start_of_day(db, user, today))
    show_weekly = weekly_tasks_visible(user.mode)
    result = []
    for task in db.scalars(select(Task).order_by(Task.id)):
        if task.period == "daily" and task.kind in daily_kinds:
            result.append(task)
        elif task.period == "weekly" and show_weekly:
            result.append(task)
    return result


def ensure_user_tasks(db: Session, user: User, today: date) -> list[UserTask]:
    """Задания текущих суток и недели; создаются лениво, прогресс берётся из журнала."""
    result = []
    for task in visible_tasks(db, user, today):
        start = period_start(task.period, today)
        user_task = db.scalar(
            select(UserTask).where(
                UserTask.user_id == user.id,
                UserTask.task_id == task.id,
                UserTask.period_start == start,
            )
        )
        if user_task is None:
            user_task = UserTask(
                user_id=user.id, task_id=task.id, period_start=start, progress=0, status="active"
            )
            db.add(user_task)
        metric = task.condition["metric"]
        if user_task.status == "active" and metric != "manual":
            value = metric_value(
                db, user.id, metric, start, period_end(task.period, start)
            )
            user_task.progress = clamp_progress(value, task.condition["target"])
        result.append(user_task)
    db.flush()
    return result


def settle_tasks(db: Session, user: User, today: date, now: datetime) -> tuple[int, list[str]]:
    """Закрывает задания, условия которых выполнены, и начисляет XP. Возвращает (XP, коды)."""
    total, codes = 0, []
    for user_task in ensure_user_tasks(db, user, today):
        task = user_task.task
        if task.condition["metric"] == "manual" or user_task.status != "active":
            continue
        if is_complete(user_task.progress, task.condition["target"]):
            user_task.status = "completed"
            total += grant(db, user.id, rules.SRC_TASK, task.xp_reward, user_task.id, now)
            codes.append(task.code)
    return total, codes


def settle_pending(db: Session, user: User, now: datetime) -> Reward:
    """Засчитывает задания, условия которых уже выполнены (например, вес записан до их выдачи)."""
    reward = Reward()
    character = user.character
    if character is None:
        return reward
    reward.task_xp, reward.tasks_completed = settle_tasks(db, user, now.date(), now)
    if reward.tasks_completed:
        _finish_rewards(db, user, character, reward, now)
    return reward


def complete_manual_task(db: Session, user: User, user_task: UserTask, now: datetime) -> Reward:
    """Подтверждение задания восстановления (прогулка, мобилизация): малая награда, один раз."""
    reward = Reward()
    character = user.character
    task = user_task.task
    if character is None or user_task.status != "active":
        return reward
    user_task.progress = task.condition["target"]
    user_task.status = "completed"
    reward.task_xp = grant(db, user.id, rules.SRC_TASK, task.xp_reward, user_task.id, now)
    reward.tasks_completed.append(task.code)
    _finish_rewards(db, user, character, reward, now)
    return reward


def get_streak_state(db: Session, user_id: int) -> tuple[Streak | None, StreakState]:
    row = db.get(Streak, user_id)
    if row is None:
        return None, StreakState()
    return row, StreakState(row.weeks, row.freezes_left, row.last_week, row.freeze_month)


def streak_view(db: Session, user: User, today: date) -> dict:
    _, state = get_streak_state(db, user.id)
    # В режиме паузы серия «заморожена» на дне начала паузы.
    as_of = user.paused_at if user.mode == "paused" and user.paused_at else today
    start = week_start(today)
    return {
        "weeks": current_streak(state, as_of),
        "freezes_left": state.freezes_left,
        "week_workouts": _journal(db, user.id, rules.SRC_WORKOUT, start, start + timedelta(7))[0],
        "weekly_goal": user.character.workouts_per_week if user.character else 0,
    }


def change_mode(db: Session, user: User, mode: str, today: date) -> None:
    """Переключает режим active/paused; при возврате сдвигает серию на длину паузы."""
    if mode == user.mode:
        return
    if mode == "paused":
        user.mode, user.paused_at = "paused", today
        return
    row, state = get_streak_state(db, user.id)
    if row is not None and user.paused_at is not None:
        row.last_week = resume_after_pause(state, user.paused_at, today).last_week
    user.mode, user.paused_at = "active", None


def achievement_stats(db: Session, user: User) -> dict[str, int]:
    """Статистика для достижений. Вес и размеры тела не используются."""
    streak = db.get(Streak, user.id)
    return {
        "workouts": _journal_total(db, user.id, rules.SRC_WORKOUT)[0],
        "sets": _journal_total(db, user.id, rules.SRC_SETS)[1] // rules.XP_PER_SET,
        "tasks": _journal_total(db, user.id, rules.SRC_TASK)[0],
        "streak_weeks": streak.weeks if streak else 0,
        "level": user.character.level if user.character else 1,
    }


def grant_achievements(db: Session, user: User, now: datetime) -> list[str]:
    """Выдаёт новые достижения и возвращает их коды."""
    have = set(db.scalars(select(UserAchievement.code).where(UserAchievement.user_id == user.id)))
    new = sorted(earned_codes(achievement_stats(db, user)) - have)
    for code in new:
        db.add(UserAchievement(user_id=user.id, code=code, earned_at=now))
    db.flush()
    return new


def _finish_rewards(
    db: Session, user: User, character: Character, reward: Reward, now: datetime
) -> None:
    """Общий хвост начислений: уровень, ранг, очки уровня и достижения."""
    reward.level_before, reward.level_after = apply_xp(character, reward.xp_gained)
    reward.rank_after = character.rank
    reward.level_points_gained = level_points_gained(reward.level_before, reward.level_after)
    reward.achievements_earned = grant_achievements(db, user, now)


def award_workout(db: Session, user: User, workout: Workout, now: datetime) -> Reward:
    """Единственное место, где начисляется XP за тренировку (вызывается из finish)."""
    character: Character | None = user.character
    if character is None:
        return Reward()
    reward = Reward(
        level_before=character.level,
        level_after=character.level,
        rank_before=character.rank,
        rank_after=character.rank,
    )
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
    reward.stat_gains = stat_gains(category_by_id[s.exercise_id] for s in workout.sets)
    for stat, value in reward.stat_gains.items():
        setattr(character, stat, getattr(character, stat) + value)
    character.discipline += rules.DISCIPLINE_PER_WORKOUT
    reward.stat_gains["discipline"] = (
        reward.stat_gains.get("discipline", 0) + rules.DISCIPLINE_PER_WORKOUT
    )

    reward.task_xp, reward.tasks_completed = settle_tasks(db, user, today, now)

    week = week_start(today)
    week_workouts = _journal(db, user.id, rules.SRC_WORKOUT, week, week + timedelta(7))[0]
    row, state = get_streak_state(db, user.id)
    if week_workouts >= character.workouts_per_week:
        gained = grant(db, user.id, rules.SRC_WEEK_GOAL, rules.XP_WEEK_GOAL, week.toordinal(), now)
        if gained:
            reward.week_xp = gained
            reward.week_closed = True
            character.discipline += rules.DISCIPLINE_PER_WEEK_CLOSED
            reward.stat_gains["discipline"] += rules.DISCIPLINE_PER_WEEK_CLOSED
            state = advance_streak(state, week, today)
            if row is None:
                row = Streak(user_id=user.id)
                db.add(row)
            row.weeks, row.freezes_left = state.weeks, state.freezes_left
            row.last_week, row.freeze_month = state.last_week, state.freeze_month
    reward.streak_weeks = current_streak(state, today)

    _finish_rewards(db, user, character, reward, now)
    return reward


def recompute_character_xp(db: Session, user: User) -> None:
    """Пересчитывает XP, уровень, ранг и очки уровня персонажа из журнала."""
    total = db.scalar(
        select(func.coalesce(func.sum(XpEvent.amount), 0)).where(XpEvent.user_id == user.id)
    )
    if user.character:
        user.character.xp = total
        user.character.level = level_from_total_xp(total)[0]
        user.character.rank = rank_for_level(user.character.level)
        # очки уровня пока только копятся (улучшения появятся после MVP)
        user.character.level_points = (user.character.level - 1) * rules.LEVEL_POINTS_PER_LEVEL


def award_weight(db: Session, user: User, day: date, now: datetime) -> Reward:
    """XP за запись веса (раз в сутки, только за сегодня) и закрытие малого задания дня."""
    character = user.character
    reward = Reward()
    if character is None or day != now.date():
        return reward
    reward.weight_xp = grant(
        db, user.id, rules.SRC_WEIGHT, rules.XP_WEIGHT_ENTRY, day.toordinal(), now
    )
    reward.task_xp, reward.tasks_completed = settle_tasks(db, user, now.date(), now)
    _finish_rewards(db, user, character, reward, now)
    return reward
