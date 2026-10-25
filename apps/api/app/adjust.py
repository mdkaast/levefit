import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ai.provider import AdjustmentUnavailable, LLMProvider, get_llm
from app.ai.safety import InvalidAdjustment, validate_adjustment
from app.ai.schema import Adjustment, AdjustmentOut, PlanOut
from app.ai.snapshot import build_snapshot, previous_plan
from app.db import get_db
from app.deps import current_user
from app.game import utcnow
from app.game_rules import config as rules
from app.models import AiAdjustment, User, Workout
from app.schemas import AdjustRequest

log = logging.getLogger(__name__)
router = APIRouter()

MAX_ATTEMPTS = 2  # вторая попытка, если ответ не прошёл проверку


def llm_dependency() -> LLMProvider:
    try:
        return get_llm()
    except AdjustmentUnavailable:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "ai is not configured") from None


@router.post("/workouts/{workout_id}/adjust", response_model=AdjustmentOut)
def adjust_workout(
    workout_id: int,
    body: AdjustRequest | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    llm: LLMProvider = Depends(llm_dependency),
) -> AdjustmentOut:
    workout = db.scalar(
        select(Workout).where(Workout.id == workout_id, Workout.user_id == user.id)
    )
    if workout is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "workout not found")
    if workout.status != "finished":
        raise HTTPException(status.HTTP_409_CONFLICT, "finish the workout first")

    stored = db.scalar(select(AiAdjustment).where(AiAdjustment.workout_id == workout.id))
    if stored is not None:  # повторный запрос не тратит вызов модели
        return _out(stored)

    now = utcnow()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    used_today = db.scalar(
        select(func.count(AiAdjustment.id))
        .join(Workout, Workout.id == AiAdjustment.workout_id)
        .where(
            Workout.user_id == user.id,
            AiAdjustment.created_at >= day_start,
            AiAdjustment.created_at < day_start + timedelta(days=1),
        )
    )
    if used_today >= rules.AI_ADJUSTS_PER_DAY:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "daily ai limit reached")

    if body and body.plan:
        plan = {
            p.exercise_id: {"weight_kg": p.weight_kg, "sets": p.sets, "reps": p.reps}
            for p in body.plan
        }
    else:
        plan = previous_plan(db, user.id, workout.id)
    snapshot = build_snapshot(db, user, workout, plan)
    if not snapshot["exercises"]:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "no strength sets to adjust")

    adjustment = _generate_valid(llm, snapshot)

    db.add(
        AiAdjustment(
            workout_id=workout.id,
            input_snapshot=snapshot,
            decision=adjustment.decision,
            rationale=adjustment.rationale,
            result=adjustment.model_dump(),
            model=llm.model,
            created_at=now,
        )
    )
    try:
        db.commit()
    except IntegrityError:  # параллельный запрос успел сохранить решение
        db.rollback()
        stored = db.scalar(select(AiAdjustment).where(AiAdjustment.workout_id == workout.id))
        if stored is None:
            raise
        return _out(stored)
    return AdjustmentOut(**adjustment.model_dump(), health_flag=snapshot["health_flag"])


def _out(stored: AiAdjustment) -> AdjustmentOut:
    return AdjustmentOut(
        **Adjustment.model_validate(stored.result).model_dump(),
        health_flag=bool(stored.input_snapshot.get("health_flag")),
    )


@router.get("/plan", response_model=PlanOut)
def next_plan(user: User = Depends(current_user), db: Session = Depends(get_db)) -> PlanOut:
    """План следующей тренировки: последняя сохранённая рекомендация ИИ."""
    last = db.scalar(
        select(AiAdjustment)
        .join(Workout, Workout.id == AiAdjustment.workout_id)
        .where(Workout.user_id == user.id)
        .order_by(AiAdjustment.id.desc())
        .limit(1)
    )
    if last is None:
        return PlanOut(workout_id=None, items=[])
    return PlanOut(
        workout_id=last.workout_id, items=Adjustment.model_validate(last.result).next_workout
    )


def _generate_valid(llm: LLMProvider, snapshot: dict) -> Adjustment:
    for attempt in range(MAX_ATTEMPTS):
        try:
            adjustment = llm.generate_adjustment(snapshot)
            validate_adjustment(adjustment, snapshot)
            return adjustment
        except InvalidAdjustment as exc:
            log.warning("ai answer rejected (attempt %d): %s", attempt + 1, exc)
        except AdjustmentUnavailable as exc:
            log.warning("ai unavailable: %s", exc)
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "ai is temporarily unavailable"
            ) from None
    raise HTTPException(status.HTTP_502_BAD_GATEWAY, "ai returned an unusable answer")
