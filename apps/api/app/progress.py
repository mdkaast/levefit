"""Прогрессия по упражнениям: история, расчётный максимум, плато, стартовый план."""

from dataclasses import dataclass
from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.schema import NextExercise
from app.db import get_db
from app.deps import current_user
from app.engine import SetResult, session_score
from app.game_rules import config as rules
from app.models import Exercise, User, Workout, WorkoutSet

router = APIRouter()


@dataclass
class Session_:
    workout_id: int
    date: date
    top_weight_kg: float | None
    volume: float
    score: float  # расчётный максимум на 1 повторение; для упражнений без веса — повторы
    sets: list[dict]


def _session(workout_id: int, workout_date: date, sets: list[WorkoutSet]) -> Session_:
    weights = [s.weight_kg for s in sets if s.weight_kg]
    return Session_(
        workout_id=workout_id,
        date=workout_date,
        top_weight_kg=max(weights) if weights else None,
        volume=round(sum((s.weight_kg or 1) * (s.reps or 0) for s in sets), 1),
        score=session_score(tuple(SetResult(x.weight_kg, x.reps, x.rir) for x in sets)),
        sets=[{"weight_kg": s.weight_kg, "reps": s.reps, "rir": s.rir} for s in sets],
    )


def user_sessions(db: Session, user_id: int) -> dict[int, list[Session_]]:
    """Все завершённые тренировки пользователя по упражнениям, от старых к новым."""
    rows = db.execute(
        select(Workout.id, Workout.date, WorkoutSet)
        .join(WorkoutSet, WorkoutSet.workout_id == Workout.id)
        .join(Exercise, Exercise.id == WorkoutSet.exercise_id)
        .where(
            Workout.user_id == user_id,
            Workout.status == "finished",
            Exercise.category == "strength",
        )
        .order_by(Workout.date, Workout.id, WorkoutSet.set_no)
    )
    grouped: dict[tuple[int, int], tuple[date, list[WorkoutSet]]] = {}
    for workout_id, workout_date, workout_set in rows:
        grouped.setdefault((workout_set.exercise_id, workout_id), (workout_date, []))[1].append(
            workout_set
        )
    result: dict[int, list[Session_]] = {}
    for (exercise_id, workout_id), (workout_date, sets) in grouped.items():
        result.setdefault(exercise_id, []).append(_session(workout_id, workout_date, sets))
    for sessions in result.values():
        sessions.sort(key=lambda s: s.date)
    return result


def sessions_since_best(scores: list[float]) -> int:
    """Сколько последних тренировок прошло без нового лучшего результата (допуск 1%)."""
    if not scores:
        return 0
    best = max(scores)
    last_best = max(i for i, v in enumerate(scores) if v >= best * (1 - rules.PLATEAU_TOLERANCE))
    return len(scores) - 1 - last_best


def is_plateau(scores: list[float]) -> bool:
    return (
        len(scores) >= rules.PLATEAU_MIN_SESSIONS
        and max(scores, default=0) > 0
        and sessions_since_best(scores) >= rules.PLATEAU_SESSIONS_WITHOUT_GAIN
    )


def exercise_context(sessions: list[Session_]) -> dict:
    """Компактная история по упражнению для модели: последние тренировки и признак плато."""
    scores = [s.score for s in sessions]
    return {
        "recent_sessions": [
            {
                "date": s.date.isoformat(),
                "top_weight_kg": s.top_weight_kg,
                "volume": s.volume,
                "score": s.score,
                "sets": s.sets,
            }
            for s in sessions[-rules.AI_HISTORY_SESSIONS :]
        ],
        "sessions_total": len(sessions),
        "sessions_without_gain": sessions_since_best(scores),
        "plateau": is_plateau(scores),
    }


class ProgressPoint(BaseModel):
    date: date
    top_weight_kg: float | None
    volume: float
    score: float


class ExerciseProgress(BaseModel):
    exercise_id: int
    name: str
    points: list[ProgressPoint]
    plateau: bool
    sessions_without_gain: int


@router.get("/progress/exercises", response_model=list[ExerciseProgress])
def exercise_progress(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[ExerciseProgress]:
    sessions = user_sessions(db, user.id)
    names = {
        e.id: e.name for e in db.scalars(select(Exercise).where(Exercise.id.in_(sessions.keys())))
    }
    items = []
    for exercise_id, rows in sessions.items():
        scores = [s.score for s in rows]
        items.append(
            ExerciseProgress(
                exercise_id=exercise_id,
                name=names.get(exercise_id, "?"),
                points=[
                    ProgressPoint(
                        date=s.date, top_weight_kg=s.top_weight_kg, volume=s.volume, score=s.score
                    )
                    for s in rows[-rules.PROGRESS_POINTS :]
                ],
                plateau=is_plateau(scores),
                sessions_without_gain=sessions_since_best(scores),
            )
        )
    items.sort(key=lambda i: (-len(i.points), i.name))
    return items


def starter_plan(db: Session, user: User) -> list[NextExercise]:
    """План первой тренировки: первый день рекомендованного шаблона (без каталога — запасной)."""
    if user.character is None:
        return []
    from_catalog = _starter_from_template(db, user)
    return from_catalog if from_catalog else _legacy_starter_plan(db, user)


def _starter_from_template(db: Session, user: User) -> list[NextExercise]:
    from app import programs  # локально: programs зависит от моделей и каталога

    rec = programs.recommend_for(db, user)
    if rec is None:
        return []
    usable, _ = programs.usable_template(db, rec["primary"])
    try:
        result = programs.resolve_for_user(db, usable, rec["profile"])
    except KeyError:
        return []
    slugs = [s["slug"] for d in result["resolved"]["days"][:1] for s in d["slots"] if s["slug"]]
    by_slug = {
        e.slug: e
        for e in db.scalars(
            select(Exercise).where(Exercise.slug.in_(slugs), Exercise.category == "strength")
        )
    }
    plan: list[NextExercise] = []
    for item in result["resolved"]["days"][0]["slots"]:
        slot, slug = item["slot"], item["slug"]
        exercise = by_slug.get(slug) if slug else None
        if (
            exercise is None
            or slot["progression"] in ("time", "warmup")
            or exercise.load_type == "isometric_time"
        ):
            continue
        plan.append(
            NextExercise(
                exercise_id=exercise.id,
                name=exercise.name,
                target_weight_kg=None,
                sets=slot["sets"][0],
                reps=slot["reps"][1],
            )
        )
        if len(plan) >= rules.STARTER_MAX_EXERCISES:
            break
    return plan


def _legacy_starter_plan(db: Session, user: User) -> list[NextExercise]:
    """План по целевым мышцам из прежнего справочника (если каталог ещё не загружен)."""
    character = user.character
    if character is None:
        return []
    bodyweight_only = character.equipment in ("home", "none")
    catalog = list(
        db.scalars(
            select(Exercise)
            .where(Exercise.category == "strength", Exercise.owner_id.is_(None))
            .order_by(Exercise.id)
        )
    )
    muscles = list(character.target_muscles or rules.STARTER_DEFAULT_MUSCLES)
    reps = rules.STARTER_REPS.get(character.goal or "", rules.STARTER_DEFAULT_REPS)
    sets = max(1, rules.STARTER_SETS - (1 if character.experience == "beginner" else 0))

    plan: list[NextExercise] = []
    for muscle in muscles:
        for exercise in catalog:
            if exercise.muscle_group != muscle or exercise.name == "Планка":
                continue
            if bodyweight_only and exercise.name not in rules.BODYWEIGHT_EXERCISES:
                continue
            plan.append(
                NextExercise(
                    exercise_id=exercise.id,
                    name=exercise.name,
                    target_weight_kg=None,
                    sets=sets,
                    reps=reps,
                )
            )
            break
        if len(plan) >= rules.STARTER_MAX_EXERCISES:
            break
    return plan
