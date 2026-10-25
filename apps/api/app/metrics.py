from datetime import date as date_type
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_user
from app.game import award_weight, utcnow
from app.game_rules import config as rules
from app.models import BodyMetric, User

router = APIRouter()


class WeightIn(BaseModel):
    weight_kg: float = Field(ge=rules.MIN_WEIGHT_KG, le=rules.MAX_WEIGHT_KG)
    date: date_type | None = None


class WeightOut(BaseModel):
    model_config = {"from_attributes": True}

    date: date_type
    weight_kg: float


class WeightSaved(WeightOut):
    xp_gained: int


@router.put("/metrics/weight", response_model=WeightSaved)
def save_weight(
    body: WeightIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> WeightSaved:
    """Одна запись на дату: повторная запись за ту же дату заменяет значение."""
    now = utcnow()
    day = body.date or now.date()
    if day > now.date():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "date is in the future")
    if day < now.date() - timedelta(days=rules.MAX_WEIGHT_BACKDATE_DAYS):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "date is too old")

    entry = db.scalar(
        select(BodyMetric).where(BodyMetric.user_id == user.id, BodyMetric.date == day)
    )
    if entry is None:
        entry = BodyMetric(user_id=user.id, date=day, weight_kg=body.weight_kg)
        db.add(entry)
    else:
        entry.weight_kg = body.weight_kg
    gained = award_weight(db, user, day, now)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "concurrent update, try again") from None
    return WeightSaved(date=entry.date, weight_kg=entry.weight_kg, xp_gained=gained)


@router.get("/metrics/weight", response_model=list[WeightOut])
def list_weight(
    date_from: date_type | None = Query(default=None, alias="from"),
    date_to: date_type | None = Query(default=None, alias="to"),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[BodyMetric]:
    today = utcnow().date()
    end = date_to or today
    start = date_from or end - timedelta(days=rules.DEFAULT_WEIGHT_RANGE_DAYS)
    if start > end:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "from is after to")
    query = (
        select(BodyMetric)
        .where(BodyMetric.user_id == user.id, BodyMetric.date >= start, BodyMetric.date <= end)
        .order_by(BodyMetric.date)
    )
    return list(db.scalars(query))
