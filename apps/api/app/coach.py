"""База знаний тренера: правила владельца, оценки пользователей, предложения ИИ на одобрение."""

import hmac
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.adjust import llm_dependency
from app.ai.provider import AdjustmentUnavailable, LLMProvider
from app.config import settings
from app.db import get_db
from app.deps import current_user
from app.game import utcnow
from app.game_rules import config as rules
from app.models import AdjustmentFeedback, AiAdjustment, CoachRule, User, Workout

router = APIRouter()


def require_admin_key(x_admin_key: str = Header(default="")) -> None:
    key = settings.admin_api_key
    if not key or not hmac.compare_digest(x_admin_key, key):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid admin key")


admin = Depends(require_admin_key)


class FeedbackIn(BaseModel):
    rating: Literal["fits", "too_hard", "too_easy"]


class RuleIn(BaseModel):
    text: str = Field(min_length=3, max_length=500)


class RuleStatusIn(BaseModel):
    status: Literal["approved", "rejected"]


class RuleOut(BaseModel):
    id: int
    text: str
    status: str
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("/workouts/{workout_id}/adjust/feedback", status_code=status.HTTP_204_NO_CONTENT)
def rate_adjustment(
    workout_id: int,
    body: FeedbackIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> None:
    adjustment = db.scalar(
        select(AiAdjustment)
        .join(Workout, Workout.id == AiAdjustment.workout_id)
        .where(Workout.id == workout_id, Workout.user_id == user.id)
    )
    if adjustment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no recommendation for this workout")
    existing = db.scalar(
        select(AdjustmentFeedback).where(AdjustmentFeedback.adjustment_id == adjustment.id)
    )
    if existing is not None:
        existing.rating = body.rating
    else:
        db.add(AdjustmentFeedback(adjustment_id=adjustment.id, rating=body.rating))
    try:
        db.commit()
    except IntegrityError:  # параллельная оценка: достаточно уже сохранённой
        db.rollback()


@router.get("/admin/coach/rules", response_model=list[RuleOut], dependencies=[admin])
def list_rules(status_filter: str | None = None, db: Session = Depends(get_db)) -> list[CoachRule]:
    query = select(CoachRule).order_by(CoachRule.id)
    if status_filter:
        query = query.where(CoachRule.status == status_filter)
    return list(db.scalars(query))


@router.post(
    "/admin/coach/rules",
    response_model=RuleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin],
)
def add_rule(body: RuleIn, db: Session = Depends(get_db)) -> CoachRule:
    """Правило владельца сразу одобрено."""
    rule = CoachRule(text=body.text.strip(), status="approved", source="owner", created_at=utcnow())
    db.add(rule)
    db.commit()
    return rule


@router.patch("/admin/coach/rules/{rule_id}", response_model=RuleOut, dependencies=[admin])
def set_rule_status(rule_id: int, body: RuleStatusIn, db: Session = Depends(get_db)) -> CoachRule:
    rule = db.get(CoachRule, rule_id)
    if rule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "rule not found")
    rule.status = body.status
    db.commit()
    return rule


@router.post("/admin/coach/learn", response_model=list[RuleOut], dependencies=[admin])
def learn(
    db: Session = Depends(get_db), llm: LLMProvider = Depends(llm_dependency)
) -> list[CoachRule]:
    """ИИ предлагает правила по оценкам; они ждут одобрения и в промпт сами не попадают."""
    rows = db.execute(
        select(AiAdjustment.decision, AdjustmentFeedback.rating, func.count())
        .join(AdjustmentFeedback, AdjustmentFeedback.adjustment_id == AiAdjustment.id)
        .group_by(AiAdjustment.decision, AdjustmentFeedback.rating)
    ).all()
    if sum(count for _, _, count in rows) < rules.COACH_MIN_FEEDBACK_TO_LEARN:
        raise HTTPException(status.HTTP_409_CONFLICT, "not enough feedback yet")
    by_decision: dict[str, dict[str, int]] = {}
    for decision, rating, count in rows:
        by_decision.setdefault(decision, {})[rating] = count
    existing = list(db.scalars(select(CoachRule.text).where(CoachRule.status != "rejected")))
    try:
        proposals = llm.propose_rules({"by_decision": by_decision, "existing_rules": existing})
    except AdjustmentUnavailable:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "ai is temporarily unavailable"
        ) from None
    created = []
    for text in proposals.rules[: rules.COACH_MAX_PROPOSALS]:
        text = text.strip()[:500]
        if len(text) >= 3 and text not in existing:
            rule = CoachRule(text=text, status="proposed", source="ai", created_at=utcnow())
            db.add(rule)
            created.append(rule)
    db.commit()
    return created
