"""Цикл тренировки: оценка упражнения, пропуски, ручная правка решения движка."""

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.adjust import _out
from app.ai.schema import Adjustment, AdjustmentOut
from app.db import get_db
from app.deps import current_user
from app.game import utcnow
from app.models import AiAdjustment, Exercise, ExerciseRating, SkippedSession, User, Workout
from app.progress import user_sessions

router = APIRouter()


class RatingIn(BaseModel):
    rating: Literal["easy", "normal", "hard"]
    pain: bool = False


class RatingOut(RatingIn):
    exercise_id: int


class SkipIn(BaseModel):
    kind: Literal["move", "rest"]


class SkipOut(BaseModel):
    day: str
    kind: str


class LastSetOut(BaseModel):
    weight_kg: float | None
    reps: int | None
    rir: int | None


class LastSessionOut(BaseModel):
    day: str
    top_weight_kg: float | None
    sets: list[LastSetOut]


class OverrideIn(BaseModel):
    weight_kg: float = Field(ge=0, le=1000)
    reason: str | None = Field(default=None, max_length=200)


def _own_workout(db: Session, user: User, workout_id: int) -> Workout:
    workout = db.scalar(select(Workout).where(Workout.id == workout_id, Workout.user_id == user.id))
    if workout is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "workout not found")
    return workout


@router.put("/workouts/{workout_id}/ratings/{exercise_id}", response_model=RatingOut)
def rate_exercise(
    workout_id: int,
    exercise_id: int,
    body: RatingIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> RatingOut:
    """Одна оценка на упражнение. Учитывается в решении, пока оно не принято."""
    workout = _own_workout(db, user, workout_id)
    if db.scalar(select(AiAdjustment.id).where(AiAdjustment.workout_id == workout.id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "decision is already made")
    exercise = db.get(Exercise, exercise_id)
    if exercise is None or exercise.owner_id not in (None, user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "exercise not found")
    row = db.scalar(
        select(ExerciseRating).where(
            ExerciseRating.workout_id == workout.id, ExerciseRating.exercise_id == exercise_id
        )
    )
    if row is None:
        row = ExerciseRating(workout_id=workout.id, exercise_id=exercise_id)
        db.add(row)
    row.rating, row.pain = body.rating, body.pain
    db.commit()
    return RatingOut(exercise_id=exercise_id, rating=row.rating, pain=row.pain)


@router.get("/workouts/{workout_id}/ratings", response_model=list[RatingOut])
def list_ratings(
    workout_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[RatingOut]:
    workout = _own_workout(db, user, workout_id)
    rows = db.scalars(select(ExerciseRating).where(ExerciseRating.workout_id == workout.id))
    return [RatingOut(exercise_id=r.exercise_id, rating=r.rating, pain=r.pain) for r in rows]


@router.post("/skips", response_model=SkipOut, status_code=status.HTTP_201_CREATED)
def skip_today(
    body: SkipIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> SkipOut:
    """Пропуск тренировки: перенос или засчитанный отдых. Ничего не отнимает (XP и серия целы)."""
    today = utcnow().date()
    row = db.scalar(
        select(SkippedSession).where(SkippedSession.user_id == user.id, SkippedSession.day == today)
    )
    if row is None:
        row = SkippedSession(user_id=user.id, day=today, kind=body.kind)
        db.add(row)
    row.kind = body.kind
    db.commit()
    return SkipOut(day=today.isoformat(), kind=row.kind)


@router.delete("/skips/today", status_code=status.HTTP_204_NO_CONTENT)
def undo_skip(user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    """Отмена пропуска: можно передумать и всё-таки потренироваться."""
    row = db.scalar(
        select(SkippedSession).where(
            SkippedSession.user_id == user.id, SkippedSession.day == utcnow().date()
        )
    )
    if row is not None:
        db.delete(row)
        db.commit()


@router.patch("/workouts/{workout_id}/adjust/exercise/{exercise_id}", response_model=AdjustmentOut)
def override_decision(
    workout_id: int,
    exercise_id: int,
    body: OverrideIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> AdjustmentOut:
    """«Изменить» в итоге: пользователь сам задаёт вес на следующий раз. Правка пишется в журнал."""
    workout = _own_workout(db, user, workout_id)
    stored = db.scalar(select(AiAdjustment).where(AiAdjustment.workout_id == workout.id))
    if stored is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "decision not found")
    result = Adjustment.model_validate(stored.result)
    item = next((i for i in result.next_workout if i.exercise_id == exercise_id), None)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "exercise is not in the decision")
    previous = item.target_weight_kg
    item.target_weight_kg = body.weight_kg
    stored.result = result.model_dump()
    stored.overrides = [
        *(stored.overrides or []),
        {
            "exercise_id": exercise_id,
            "from_weight_kg": previous,
            "to_weight_kg": body.weight_kg,
            "reason": body.reason,
            "at": datetime.now(UTC).isoformat(),
        },
    ]
    flag_modified(stored, "result")
    flag_modified(stored, "overrides")
    db.commit()
    return _out(stored)


@router.get("/exercises/{exercise_id}/last", response_model=LastSessionOut | None)
def last_session(
    exercise_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> LastSessionOut | None:
    """Последняя завершённая тренировка по упражнению: «призрак» прошлой попытки на экране."""
    exercise = db.get(Exercise, exercise_id)
    if exercise is None or exercise.owner_id not in (None, user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "exercise not found")
    sessions = user_sessions(db, user.id).get(exercise_id, [])
    if not sessions:
        return None
    last = sessions[-1]
    return LastSessionOut(
        day=last.date.isoformat(),
        top_weight_kg=last.top_weight_kg,
        sets=[LastSetOut(**s) for s in last.sets],
    )
