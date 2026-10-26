"""Направления, акценты и недельный план: профиль → неделя → «Сегодня» (E1–E4, E10)."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import week
from app.content.directions import (
    ACCENT_MUSCLES,
    DIRECTIONS,
    MAX_ACCENT_MUSCLES,
    MAX_DAYS_PER_DIRECTION,
    MAX_TRAINING_DAYS,
    accent_options,
)
from app.db import get_db
from app.deps import current_user
from app.models import User

router = APIRouter()


class DirectionItem(BaseModel):
    direction: str
    days: int = Field(ge=0, le=MAX_DAYS_PER_DIRECTION)


class DirectionsIn(BaseModel):
    items: list[DirectionItem] = Field(min_length=1, max_length=len(DIRECTIONS))


class AccentIn(BaseModel):
    direction: str
    selection: list[str] = Field(max_length=MAX_ACCENT_MUSCLES)


class PreviewIn(BaseModel):
    directions: list[DirectionItem] | None = None
    accent: AccentIn | None = None


def _today() -> date:
    return week.today()


def _catalog() -> list[dict[str, Any]]:
    return [
        {
            "key": key,
            "name": info["name"],
            "kind": info["kind"],
            "accent_kind": info["accent"],
            "default_days": info["default_days"],
            "options": accent_options(key),
            "verified": info["kind"] == "strength",
        }
        for key, info in DIRECTIONS.items()
    ]


def _state(db: Session, user: User) -> dict[str, Any]:
    today = _today()
    saved = week.saved_directions(db, user)
    current = week.effective_directions(db, user)
    return {
        "catalog": _catalog(),
        "muscles": [{"key": k, "name": v["name"]} for k, v in ACCENT_MUSCLES.items()],
        "mine": [{"direction": d, "days": n} for d, n in current],
        "saved": bool(saved),
        "follows_week": bool(saved),
        "total_days": sum(n for d, n in current if d != "universal"),
        "max_days": MAX_TRAINING_DAYS,
        "accents": {
            d: {
                "current": week.accent_for(db, user, d, week.monday_of(today)),
                "next": week.accent_for(db, user, d, week.next_monday(today)),
            }
            for d, _ in current
        },
        "pending": week.pending_accent(db, user, today),
        "next_monday": week.next_monday(today).isoformat(),
    }


@router.get("/directions")
def get_directions(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    return _state(db, user)


@router.put("/me/directions")
def put_directions(
    body: DirectionsIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Сохраняет направления; идущая неделя не меняется, новая расстановка с понедельника."""
    try:
        week.set_directions(db, user, [(i.direction, i.days) for i in body.items], _today())
    except week.InvalidChange as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    db.commit()
    return _state(db, user)


@router.put("/me/accent")
def put_accent(
    body: AccentIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        start = week.set_accent(db, user, body.direction, body.selection, _today())
    except week.InvalidChange as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    db.commit()
    return {"effective_from": start.isoformat(), **_state(db, user)}


@router.get("/week")
def get_week(
    offset: int = Query(default=0, ge=0, le=1),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Текущая неделя (замораживается при первом запросе) или предварительная следующая."""
    today = _today()
    if offset == 1:
        spec = week.upcoming_week(db, user, today)
    else:
        spec = week.ensure_week(db, user, week.monday_of(today))
        db.commit()
    return {
        "offset": offset,
        "today": today.isoformat(),
        "follows_week": week.follows_week(db, user),
        **spec,
    }


@router.post("/week/preview")
def preview_week(
    body: PreviewIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    """«До / после» для следующей недели; ничего не сохраняет."""
    directions = [(i.direction, i.days) for i in body.directions] if body.directions else None
    accent = (body.accent.direction, body.accent.selection) if body.accent else None
    try:
        result = week.preview(db, user, _today(), directions, accent)
    except week.InvalidChange as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    result.pop("before")
    after = result.pop("after")
    result["after_warnings"] = after["warnings"]
    result["after_days"] = after["days"]
    return result
