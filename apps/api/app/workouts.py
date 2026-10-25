from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_user
from app.models import Exercise, User, Workout, WorkoutSet
from app.schemas import (
    ExerciseCreate,
    ExerciseOut,
    SetCreate,
    SetOut,
    WorkoutCreate,
    WorkoutFinish,
    WorkoutOut,
    WorkoutSummary,
)

router = APIRouter()


def _get_workout(db: Session, user: User, workout_id: int) -> Workout:
    workout = db.scalar(
        select(Workout).where(Workout.id == workout_id, Workout.user_id == user.id)
    )
    if workout is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "workout not found")
    return workout


@router.get("/exercises", response_model=list[ExerciseOut])
def list_exercises(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[Exercise]:
    query = (
        select(Exercise)
        .where(or_(Exercise.owner_id.is_(None), Exercise.owner_id == user.id))
        .order_by(Exercise.category, Exercise.name)
    )
    return list(db.scalars(query))


@router.post("/exercises", response_model=ExerciseOut, status_code=status.HTTP_201_CREATED)
def create_exercise(
    body: ExerciseCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Exercise:
    exercise = Exercise(owner_id=user.id, **body.model_dump())
    db.add(exercise)
    db.commit()
    return exercise


@router.post("/workouts", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
def create_workout(
    body: WorkoutCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Workout:
    workout = Workout(
        user_id=user.id,
        title=body.title.strip() or "Тренировка",
        date=body.date or datetime.now(UTC).date(),
        status=body.status,
        notes=body.notes,
    )
    db.add(workout)
    db.commit()
    return workout


@router.get("/workouts", response_model=list[WorkoutSummary])
def list_workouts(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[WorkoutSummary]:
    rows = db.execute(
        select(Workout, func.count(WorkoutSet.id))
        .outerjoin(WorkoutSet, WorkoutSet.workout_id == Workout.id)
        .where(Workout.user_id == user.id)
        .group_by(Workout.id)
        .order_by(Workout.date.desc(), Workout.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [
        WorkoutSummary(
            id=w.id,
            date=w.date,
            title=w.title,
            status=w.status,
            duration_min=w.duration_min,
            sets_count=count,
        )
        for w, count in rows
    ]


@router.get("/workouts/{workout_id}", response_model=WorkoutOut)
def get_workout(
    workout_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Workout:
    return _get_workout(db, user, workout_id)


@router.post(
    "/workouts/{workout_id}/sets", response_model=SetOut, status_code=status.HTTP_201_CREATED
)
def add_set(
    workout_id: int,
    body: SetCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> WorkoutSet:
    workout = _get_workout(db, user, workout_id)
    if workout.status == "finished":
        raise HTTPException(status.HTTP_409_CONFLICT, "workout is finished")

    exercise = db.get(Exercise, body.exercise_id)
    if exercise is None or exercise.owner_id not in (None, user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "exercise not found")

    if exercise.category == "cardio":
        if body.duration_s is None and body.distance_m is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "duration or distance required"
            )
    elif exercise.category == "strength":
        if body.reps is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "reps required")
    elif body.duration_s is None and body.reps is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "duration or reps required")

    last_no = db.scalar(
        select(func.max(WorkoutSet.set_no)).where(
            WorkoutSet.workout_id == workout.id, WorkoutSet.exercise_id == exercise.id
        )
    )
    workout_set = WorkoutSet(
        workout_id=workout.id, set_no=(last_no or 0) + 1, **body.model_dump()
    )
    workout.status = "in_progress"
    db.add(workout_set)
    db.commit()
    return workout_set


@router.post("/workouts/{workout_id}/finish", response_model=WorkoutOut)
def finish_workout(
    workout_id: int,
    body: WorkoutFinish | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Workout:
    workout = _get_workout(db, user, workout_id)
    if workout.status == "finished":
        raise HTTPException(status.HTTP_409_CONFLICT, "workout is already finished")
    if not workout.sets:
        raise HTTPException(status.HTTP_409_CONFLICT, "workout has no sets")
    workout.status = "finished"
    if body and body.duration_min:
        workout.duration_min = body.duration_min
    db.commit()
    return workout
