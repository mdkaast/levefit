"""Админ-панель владельца: доступ, аналитика, сведения об ИИ, запросы на изменение приложения."""

import hmac
from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.deps import bearer
from app.game import utcnow
from app.models import (
    AdjustmentFeedback,
    AiAdjustment,
    ChangeRequest,
    CoachRule,
    User,
    Workout,
    WorkoutSet,
)
from app.security import InvalidToken, verify_access_token


def admin_telegram_ids() -> set[int]:
    return {int(x) for x in settings.admin_telegram_ids.replace(" ", "").split(",") if x.isdigit()}


def is_admin(user: User) -> bool:
    return user.telegram_id in admin_telegram_ids()


def require_admin(
    x_admin_key: str = Header(default=""),
    credentials=Depends(bearer),
    db: Session = Depends(get_db),
) -> None:
    """Пускает по ключу сервера или по токену пользователя из списка ADMIN_TELEGRAM_IDS."""
    key = settings.admin_api_key
    if key and hmac.compare_digest(x_admin_key, key):
        return
    if credentials is not None:
        try:
            user_id = verify_access_token(credentials.credentials, settings.app_secret)
        except InvalidToken:
            user_id = None
        user = db.get(User, user_id) if user_id else None
        if user is not None and is_admin(user):
            return
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "admin access required")


router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])

ChangeStatus = Literal["draft", "sent", "done"]


class RequestIn(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    prompt: str = Field(min_length=10, max_length=8000)


class RequestPatch(BaseModel):
    status: ChangeStatus


class RequestOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    prompt: str
    status: str
    created_at: datetime


def _count(db: Session, query) -> int:
    return db.scalar(query) or 0


@router.get("/stats")
def stats(db: Session = Depends(get_db)) -> dict:
    now = utcnow()
    week = now - timedelta(days=7)
    today = now.date()
    finished = Workout.status == "finished"

    daily = {
        d: n
        for d, n in db.execute(
            select(Workout.date, func.count())
            .where(finished, Workout.date > today - timedelta(days=14))
            .group_by(Workout.date)
        )
    }
    by_decision = [
        {"decision": d, "count": n}
        for d, n in db.execute(
            select(AiAdjustment.decision, func.count()).group_by(AiAdjustment.decision)
        )
    ]
    ratings = {
        r: n
        for r, n in db.execute(
            select(AdjustmentFeedback.rating, func.count()).group_by(AdjustmentFeedback.rating)
        )
    }
    rule_counts = {
        s: n
        for s, n in db.execute(select(CoachRule.status, func.count()).group_by(CoachRule.status))
    }
    return {
        "users": {
            "total": _count(db, select(func.count(User.id))),
            "new_7d": _count(db, select(func.count(User.id)).where(User.created_at >= week)),
            "active_7d": _count(
                db,
                select(func.count(func.distinct(Workout.user_id))).where(
                    finished, Workout.date > today - timedelta(days=7)
                ),
            ),
            "paused": _count(db, select(func.count(User.id)).where(User.mode == "paused")),
        },
        "workouts": {
            "finished": _count(db, select(func.count(Workout.id)).where(finished)),
            "finished_7d": _count(
                db,
                select(func.count(Workout.id)).where(
                    finished, Workout.date > today - timedelta(days=7)
                ),
            ),
            "sets": _count(db, select(func.count(WorkoutSet.id))),
            "daily": [
                {
                    "date": (today - timedelta(days=i)).isoformat(),
                    "count": daily.get(today - timedelta(days=i), 0),
                }
                for i in range(13, -1, -1)
            ],
        },
        "ai": {
            "total": _count(db, select(func.count(AiAdjustment.id))),
            "last_7d": _count(
                db, select(func.count(AiAdjustment.id)).where(AiAdjustment.created_at >= week)
            ),
            "by_decision": by_decision,
            "ratings": {k: ratings.get(k, 0) for k in ("fits", "too_hard", "too_easy")},
            "rules": {k: rule_counts.get(k, 0) for k in ("approved", "proposed", "rejected")},
            "configured": bool(settings.anthropic_api_key),
            "model": settings.llm_model,
        },
    }


@router.get("/ai/recent")
def recent_adjustments(limit: int = 20, db: Session = Depends(get_db)) -> list[dict]:
    """Последние решения ИИ без персональных данных: решение, объяснение, оценка."""
    rows = db.execute(
        select(AiAdjustment, AdjustmentFeedback.rating)
        .outerjoin(AdjustmentFeedback, AdjustmentFeedback.adjustment_id == AiAdjustment.id)
        .order_by(AiAdjustment.id.desc())
        .limit(max(1, min(limit, 100)))
    )
    return [
        {
            "id": a.id,
            "created_at": a.created_at,
            "decision": a.decision,
            "rationale": a.rationale,
            "model": a.model,
            "rating": rating,
            "rules_used": len(a.input_snapshot.get("coach_rules") or []),
        }
        for a, rating in rows
    ]


@router.get("/requests", response_model=list[RequestOut])
def list_requests(db: Session = Depends(get_db)) -> list[ChangeRequest]:
    return list(db.scalars(select(ChangeRequest).order_by(ChangeRequest.id.desc())))


@router.post("/requests", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def add_request(body: RequestIn, db: Session = Depends(get_db)) -> ChangeRequest:
    item = ChangeRequest(
        title=body.title.strip(), prompt=body.prompt.strip(), status="draft", created_at=utcnow()
    )
    db.add(item)
    db.commit()
    return item


@router.patch("/requests/{request_id}", response_model=RequestOut)
def set_request_status(
    request_id: int, body: RequestPatch, db: Session = Depends(get_db)
) -> ChangeRequest:
    item = db.get(ChangeRequest, request_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "request not found")
    item.status = body.status
    db.commit()
    return item


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)) -> None:
    item = db.get(ChangeRequest, request_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "request not found")
    db.delete(item)
    db.commit()
