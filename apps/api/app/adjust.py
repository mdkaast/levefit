"""Решение о нагрузке после тренировки: числа считает движок (app/engine), ИИ-тренер объясняет."""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import week
from app.ai.provider import AdjustmentUnavailable, LLMProvider, get_llm
from app.ai.safety import InvalidExplanation, validate_explanation
from app.ai.schema import (
    Adjustment,
    AdjustmentOut,
    EngineDecisionOut,
    Explanation,
    NextExercise,
    PlanOut,
)
from app.ai.snapshot import build_snapshot, previous_plan
from app.db import get_db
from app.decisions import (
    engine_inputs,
    plan_adjusted_for_light_day,
    plan_adjusted_for_return,
    to_adjustment,
)
from app.deps import current_user
from app.engine import decide_session
from app.engine.explain import allowed_weights, describe, template_explanation
from app.game import utcnow
from app.game_rules import config as rules
from app.models import AiAdjustment, SkippedSession, User, Workout
from app.progress import starter_plan
from app.schemas import AdjustRequest

log = logging.getLogger(__name__)
router = APIRouter()

MAX_ATTEMPTS = 2  # вторая попытка, если текст ИИ-тренера не прошёл проверку


def llm_dependency() -> LLMProvider | None:
    """ИИ-тренер необязателен: без ключа решение остаётся, объяснение берётся из шаблона."""
    try:
        return get_llm()
    except AdjustmentUnavailable:
        return None


@router.post("/workouts/{workout_id}/adjust", response_model=AdjustmentOut)
def adjust_workout(
    workout_id: int,
    body: AdjustRequest | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    llm: LLMProvider | None = Depends(llm_dependency),
) -> AdjustmentOut:
    workout = db.scalar(select(Workout).where(Workout.id == workout_id, Workout.user_id == user.id))
    if workout is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "workout not found")
    if workout.status != "finished":
        raise HTTPException(status.HTTP_409_CONFLICT, "finish the workout first")

    stored = db.scalar(select(AiAdjustment).where(AiAdjustment.workout_id == workout.id))
    if stored is not None:  # повторный запрос возвращает то же решение
        return _out(stored)

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

    items, ctx = engine_inputs(db, user, workout, plan, snapshot)
    session = decide_session(items, ctx)
    health_flag = bool(snapshot["health_flag"])

    changes, rationale = template_explanation(session, health_flag=health_flag)
    explained_by = "template"
    usage: dict[str, int] = {}
    now = utcnow()
    if llm is not None and _llm_quota_left(db, user, now):
        payload = {
            "overall": session.overall,
            "engine_decisions": describe(session),
            "deload_signals": list(session.deload_signals),
            "context": snapshot,
        }
        explanation = _explain(llm, payload, health_flag, allowed_weights(session), usage)
        if explanation is not None:
            changes, rationale, explained_by = explanation.changes, explanation.rationale, "llm"

    adjustment = to_adjustment(session, changes, rationale)
    db.add(
        AiAdjustment(
            workout_id=workout.id,
            input_snapshot=snapshot,
            decision=adjustment.decision,
            rationale=adjustment.rationale,
            result=adjustment.model_dump(),
            model=llm.model if explained_by == "llm" and llm is not None else "engine",
            engine_version=session.rules_version,
            engine_decisions=describe(session),
            explained_by=explained_by,
            input_tokens=usage.get("input"),
            output_tokens=usage.get("output"),
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
    return AdjustmentOut(
        **adjustment.model_dump(),
        health_flag=health_flag,
        engine_version=session.rules_version,
        explained_by=explained_by,
        engine=_engine_out(describe(session)),
    )


def _llm_quota_left(db: Session, user: User, now) -> bool:
    """Объяснения ИИ ограничены в сутки; решение движка от лимита не зависит."""
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    used = db.scalar(
        select(func.count(AiAdjustment.id))
        .join(Workout, Workout.id == AiAdjustment.workout_id)
        .where(
            Workout.user_id == user.id,
            AiAdjustment.explained_by == "llm",
            AiAdjustment.created_at >= day_start,
            AiAdjustment.created_at < day_start + timedelta(days=1),
        )
    )
    return (used or 0) < rules.AI_ADJUSTS_PER_DAY


def _explain(
    llm: LLMProvider,
    payload: dict,
    health_flag: bool,
    weights: set[float],
    usage: dict[str, int],
) -> Explanation | None:
    """Текст ИИ-тренера или None, если он недоступен или два раза нарушил правила."""
    for attempt in range(MAX_ATTEMPTS):
        try:
            explanation = llm.explain(payload)
            _add_usage(llm, usage)
            validate_explanation(explanation, health_flag=health_flag, allowed_weights=weights)
            return explanation
        except InvalidExplanation as exc:
            _add_usage(llm, usage)
            log.warning("coach text rejected (attempt %d): %s", attempt + 1, exc)
        except AdjustmentUnavailable as exc:
            log.warning("ai unavailable, using template: %s", exc)
            return None
    return None


def _add_usage(llm: LLMProvider, usage: dict[str, int]) -> None:
    """Суммирует токены последнего запроса (повторная попытка тоже стоит денег)."""
    last = getattr(llm, "last_usage", None)
    if not last:
        return
    usage["input"] = usage.get("input", 0) + last[0]
    usage["output"] = usage.get("output", 0) + last[1]


def _engine_out(raw: list[dict] | None) -> list[EngineDecisionOut]:
    fields = EngineDecisionOut.model_fields
    return [
        EngineDecisionOut(**{k: v for k, v in item.items() if k in fields}) for item in raw or []
    ]


def _out(stored: AiAdjustment) -> AdjustmentOut:
    return AdjustmentOut(
        **Adjustment.model_validate(stored.result).model_dump(),
        health_flag=bool(stored.input_snapshot.get("health_flag")),
        engine_version=stored.engine_version,
        explained_by=stored.explained_by,
        engine=_engine_out(stored.engine_decisions),
    )


@router.get("/plan", response_model=PlanOut)
def next_plan(
    sleep: int | None = Query(default=None, ge=1, le=5),
    energy: int | None = Query(default=None, ge=1, le=5),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> PlanOut:
    """План следующей тренировки: решение движка (или стартовый план) с поправками на сегодня."""
    last = db.scalar(
        select(AiAdjustment)
        .join(Workout, Workout.id == AiAdjustment.workout_id)
        .where(Workout.user_id == user.id)
        .order_by(AiAdjustment.id.desc())
        .limit(1)
    )
    today = week.today()
    session_info = None
    from_week = week.follows_week(db, user)
    planned, planned_day = week.planned_session(db, user, today) if from_week else (None, None)
    if planned is not None and planned_day is not None:
        # Перешёл на программу: состав из недельного плана, веса из решений движка.
        items = [NextExercise(**line) for line in week.plan_items(db, user, planned)]
        source, workout_id = "week", (last.workout_id if last else None)
        session_info = {
            "title": planned["title"],
            "direction": planned["direction"],
            "kind": planned["kind"],
            "minutes": planned["minutes"],
            "blocks": planned["blocks"],
            "day": planned_day.isoformat(),
            "is_today": planned_day == today,
            "verified": planned["verified"],
        }
    elif last is None:
        # Первая тренировка: решать нечего, даём стартовый план по профилю.
        items = starter_plan(db, user)
        source, workout_id = ("starter" if items else None), None
    else:
        items = Adjustment.model_validate(last.result).next_workout
        source, workout_id = "ai", last.workout_id
    items, notes = plan_adjusted_for_return(db, user, items, today)
    items, light_notes = plan_adjusted_for_light_day(db, user, items, sleep, energy)
    skipped = db.scalar(
        select(SkippedSession.kind).where(
            SkippedSession.user_id == user.id, SkippedSession.day == today
        )
    )
    return PlanOut(
        workout_id=workout_id,
        items=items,
        source=source,
        notes=notes + light_notes,
        decisions=[d["reason"] for d in (last.engine_decisions or [])][:3] if last else [],
        skipped_today=skipped,
        session=session_info,
    )
