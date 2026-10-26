"""Связка движка с базой: собирает входные данные, запускает правила, готовит поправки к плану."""

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.schema import Adjustment, NextExercise
from app.engine import (
    Context,
    ExerciseInput,
    PlanTarget,
    SessionDecision,
    SessionSummary,
    SetResult,
    apply_light_day,
    apply_return,
    is_light_day,
    return_factors,
    session_score,
    step_for,
)
from app.engine import rules as R
from app.models import AiAdjustment, Exercise, ExerciseRating, SkippedSession, User, Workout
from app.progress import Session_, is_plateau, user_sessions


def _to_sets(raw: list[dict]) -> tuple[SetResult, ...]:
    return tuple(SetResult(s["weight_kg"], s["reps"], s["rir"]) for s in raw)


def _before(session: Session_, workout: Workout) -> bool:
    return (session.date, session.workout_id) < (workout.date, workout.id)


def _recent_low_readiness(db: Session, user: User, workout: Workout) -> int:
    rows = db.scalars(
        select(Workout)
        .where(Workout.user_id == user.id, Workout.status == "finished", Workout.id != workout.id)
        .where(Workout.date <= workout.date)
        .order_by(Workout.date.desc(), Workout.id.desc())
        .limit(5)
    )
    return sum(1 for w in rows if is_light_day(w.sleep_quality, w.energy))


def _recent_skips(db: Session, user: User, workout: Workout) -> int:
    since = workout.date - timedelta(days=R.SKIPS_WINDOW_DAYS)
    return (
        db.scalar(
            select(func.count(SkippedSession.id)).where(
                SkippedSession.user_id == user.id,
                SkippedSession.day >= since,
                SkippedSession.day <= workout.date,
            )
        )
        or 0
    )


def deload_due(db: Session, user: User, workout: Workout, experience: str | None) -> bool:
    """Плановая разгрузка: прошло достаточно недель с прошлой разгрузки (или с начала занятий)."""
    last_deload: date | None = db.scalar(
        select(Workout.date)
        .join(AiAdjustment, AiAdjustment.workout_id == Workout.id)
        .where(
            Workout.user_id == user.id,
            AiAdjustment.decision == "deload",
            Workout.id != workout.id,
        )
        .order_by(Workout.date.desc())
        .limit(1)
    )
    first: date | None = db.scalar(
        select(func.min(Workout.date)).where(
            Workout.user_id == user.id, Workout.status == "finished"
        )
    )
    start = last_deload or first
    if start is None:
        return False
    sessions = db.scalar(
        select(func.count(Workout.id)).where(
            Workout.user_id == user.id,
            Workout.status == "finished",
            Workout.date > start,
            Workout.date <= workout.date,
            Workout.id != workout.id,
        )
    )
    weeks = (workout.date - start).days / 7
    threshold = R.SCHEDULED_DELOAD_WEEKS.get(experience or "", R.SCHEDULED_DELOAD_DEFAULT_WEEKS)
    return weeks >= threshold and (sessions or 0) + 1 >= R.SCHEDULED_DELOAD_MIN_SESSIONS


def engine_inputs(
    db: Session, user: User, workout: Workout, plan: dict[int, dict], snapshot: dict
) -> tuple[tuple[ExerciseInput, ...], Context]:
    """Входные данные движка: сегодняшние подходы, план, история по упражнениям и контекст."""
    ids = [e["exercise_id"] for e in snapshot["exercises"]]
    exercises = {e.id: e for e in db.scalars(select(Exercise).where(Exercise.id.in_(ids)))}
    sessions = user_sessions(db, user.id)
    character = user.character
    experience = character.experience if character else None

    ratings = {
        r.exercise_id: r.rating
        for r in db.scalars(select(ExerciseRating).where(ExerciseRating.workout_id == workout.id))
    }
    items = []
    for fact in snapshot["exercises"]:
        exercise_id = fact["exercise_id"]
        today = _to_sets(fact["actual_sets"])
        previous = [s for s in sessions.get(exercise_id, []) if _before(s, workout)]
        scores = [s.score for s in previous] + [session_score(today)]
        target = plan.get(exercise_id)
        items.append(
            ExerciseInput(
                exercise_id=exercise_id,
                name=fact["name"],
                muscle_group=exercises[exercise_id].muscle_group,
                sets=today,
                plan=PlanTarget(target["weight_kg"], target["sets"], target["reps"])
                if target
                else None,
                history=tuple(
                    SessionSummary(s.date, s.top_weight_kg, s.score, _to_sets(s.sets))
                    for s in previous[-R.SCHEDULED_DELOAD_MIN_SESSIONS :]
                ),
                plateau=is_plateau(scores),
                rating=ratings.get(exercise_id),
            )
        )
    ctx = Context(
        experience=experience,
        goal=character.goal if character else None,
        age=character.age if character else None,
        health_flag=bool(snapshot["health_flag"]),
        low_readiness=bool(snapshot["low_readiness"]),
        recent_low_readiness=_recent_low_readiness(db, user, workout),
        deload_due=deload_due(db, user, workout, experience),
        recent_skips=_recent_skips(db, user, workout),
    )
    return tuple(items), ctx


def to_adjustment(session: SessionDecision, changes: list[str], rationale: str) -> Adjustment:
    return Adjustment(
        changes=changes,
        decision=session.overall,
        next_workout=[
            NextExercise(
                exercise_id=d.exercise_id,
                name=d.name,
                target_weight_kg=d.next_weight_kg,
                sets=d.next_sets,
                reps=d.rep_max,
                rep_targets=list(d.next_reps),
            )
            for d in session.exercises
        ],
        rationale=rationale,
    )


def plan_adjusted_for_return(
    db: Session, user: User, items: list[NextExercise], today: date
) -> tuple[list[NextExercise], list[str]]:
    """Если после последней тренировки был перерыв, план мягче: меньше вес и объём (4.5)."""
    last = db.scalar(
        select(func.max(Workout.date)).where(
            Workout.user_id == user.id, Workout.status == "finished"
        )
    )
    if last is None or not items:
        return items, []
    days = (today - last).days
    character = user.character
    weight_pct, volume, recalibrate = return_factors(days, character.age if character else None)
    if not weight_pct and volume == 1.0:
        return items, []
    groups = {
        e.id: e.muscle_group
        for e in db.scalars(select(Exercise).where(Exercise.id.in_([i.exercise_id for i in items])))
    }
    ctx = Context(experience=character.experience if character else None)
    adjusted = []
    for item in items:
        step = step_for(
            ExerciseInput(item.exercise_id, item.name, groups.get(item.exercise_id, ""), ()), ctx
        )
        weight, sets = apply_return(item.target_weight_kg, item.sets, step, weight_pct, volume)
        targets = (item.rep_targets or [item.reps])[:sets]
        adjusted.append(
            item.model_copy(
                update={"target_weight_kg": weight, "sets": sets, "rep_targets": targets}
            )
        )
    notes = [
        f"Перерыв {days} дн.: вес ниже на {round(weight_pct * 100)}%, "
        f"объём {round(volume * 100)}% от прежнего, пока не вернётесь в ритм."
    ]
    if recalibrate:
        notes.append("Перерыв долгий: первую тренировку считайте тестовой и подберите вес заново.")
    return adjusted, notes


def plan_adjusted_for_light_day(
    db: Session, user: User, items: list[NextExercise], sleep: int | None, energy: int | None
) -> tuple[list[NextExercise], list[str]]:
    """«Лёгкий день» по самочувствию перед тренировкой: вес −10%, на подход меньше (4.11)."""
    if not is_light_day(sleep, energy) or not items:
        return items, []
    groups = {
        e.id: e.muscle_group
        for e in db.scalars(select(Exercise).where(Exercise.id.in_([i.exercise_id for i in items])))
    }
    character = user.character
    ctx = Context(experience=character.experience if character else None)
    adjusted = []
    for item in items:
        step = step_for(
            ExerciseInput(item.exercise_id, item.name, groups.get(item.exercise_id, ""), ()), ctx
        )
        weight, sets = apply_light_day(item.target_weight_kg, item.sets, step)
        adjusted.append(
            item.model_copy(
                update={
                    "target_weight_kg": weight,
                    "sets": sets,
                    "rep_targets": (item.rep_targets or [item.reps])[:sets],
                }
            )
        )
    return adjusted, [
        "Низкое самочувствие: лёгкий день, вес ниже на 10% и на подход меньше, без рекордов."
    ]
