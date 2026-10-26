"""Питание: цель по калориям, дневник, продукты и рецепты (F2–F7, F11)."""

import datetime as dt
from datetime import timedelta
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import nutrition_calc as calc
from app.content.foods_data import FOOD_GROUPS
from app.db import get_db
from app.deps import current_user
from app.foodsource import LocalFoodSource
from app.game import utcnow
from app.models import BodyMetric, Food, FoodEntry, NutritionGoal, Recipe, User
from app.nutrition_recipes import MEAL_NAMES, TAG_NAMES, suggest

router = APIRouter()

Meal = Literal["breakfast", "lunch", "dinner", "snack"]
MEALS: tuple[str, ...] = ("breakfast", "lunch", "dinner", "snack")
MAX_DAYS_BACK = 365


# --- входные данные ------------------------------------------------------------------------


class EntryIn(BaseModel):
    date: dt.date | None = None
    meal: Meal
    food_id: int | None = None
    recipe_id: int | None = None
    grams: float | None = Field(default=None, ge=1, le=3000)
    servings: float | None = Field(default=None, ge=0.25, le=12)


class EntryPatch(BaseModel):
    meal: Meal | None = None
    grams: float | None = Field(default=None, ge=1, le=3000)
    servings: float | None = Field(default=None, ge=0.25, le=12)


class FoodIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    kcal: float = Field(ge=0, le=900)
    protein: float = Field(ge=0, le=100)
    fat: float = Field(ge=0, le=100)
    carbs: float = Field(ge=0, le=100)


class GoalIn(BaseModel):
    mode: Literal["gain", "maintain", "lose"]
    adjust_kcal: int = Field(default=0, ge=-calc.ADJUST_MAX, le=calc.ADJUST_MAX)
    restrictions: list[str] = Field(default_factory=list, max_length=len(calc.SCREENING))


# --- общие помощники -----------------------------------------------------------------------


def _day(value: dt.date | None) -> dt.date:
    today = utcnow().date()
    day = value or today
    if day > today + timedelta(days=1) or day < today - timedelta(days=MAX_DAYS_BACK):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "date out of range")
    return day


def _profile(db: Session, user: User) -> calc.Profile:
    character = user.character
    weight = db.scalar(
        select(BodyMetric.weight_kg)
        .where(BodyMetric.user_id == user.id)
        .order_by(BodyMetric.date.desc())
        .limit(1)
    )
    gender = character.gender if character else None
    return calc.Profile(
        sex=gender if gender in ("male", "female") else "other",
        age=character.age if character else None,
        height_cm=character.height_cm if character else None,
        weight_kg=weight,
        lifestyle=character.lifestyle if character else None,
    )


def _saved_goal(db: Session, user: User) -> NutritionGoal | None:
    return db.get(NutritionGoal, user.id)


def _goal_dict(goal: calc.Goal | None) -> dict[str, Any] | None:
    if goal is None:
        return None
    return {
        "mode": goal.mode,
        "kcal": goal.kcal,
        "protein_g": goal.protein_g,
        "fat_g": goal.fat_g,
        "carbs_g": goal.carbs_g,
        "bmr": goal.bmr,
        "tdee": goal.tdee,
        "floor": goal.floor,
        "delta_kcal": goal.delta_kcal,
        "adjust_kcal": goal.adjust_kcal,
        "assumptions": goal.assumptions,
        "notes": goal.notes,
        "clamped": goal.clamped,
    }


def _trend_hint(db: Session, user: User) -> str | None:
    today = utcnow().date()

    def weights(start: dt.date, end: dt.date) -> list[float]:
        rows = db.scalars(
            select(BodyMetric.weight_kg).where(
                BodyMetric.user_id == user.id, BodyMetric.date > start, BodyMetric.date <= end
            )
        )
        return list(rows)

    return calc.weight_trend_hint(
        weights(today - timedelta(days=7), today),
        weights(today - timedelta(days=14), today - timedelta(days=7)),
    )


def _entry_dict(e: FoodEntry) -> dict[str, Any]:
    return {
        "id": e.id,
        "meal": e.meal,
        "name": e.name,
        "grams": e.grams,
        "servings": e.servings,
        "food_id": e.food_id,
        "recipe_id": e.recipe_id,
        "kcal": round(e.kcal),
        "protein": round(e.protein, 1),
        "fat": round(e.fat, 1),
        "carbs": round(e.carbs, 1),
    }


def _sum(entries: list[FoodEntry]) -> dict[str, float]:
    return {
        "kcal": round(sum(e.kcal for e in entries)),
        "protein": round(sum(e.protein for e in entries), 1),
        "fat": round(sum(e.fat for e in entries), 1),
        "carbs": round(sum(e.carbs for e in entries), 1),
    }


def _food_dict(f: Food) -> dict[str, Any]:
    return {
        "id": f.id,
        "name": f.name,
        "group": f.group,
        "group_name": FOOD_GROUPS.get(f.group, ""),
        "kcal": f.kcal,
        "protein": f.protein,
        "fat": f.fat,
        "carbs": f.carbs,
        "piece_g": f.piece_g,
        "piece_name": f.piece_name,
        "own": f.owner_id is not None,
        "verified": f.verified,
    }


def _recipe_card(r: Recipe) -> dict[str, Any]:
    return {
        "id": r.id,
        "name": r.name,
        "minutes": r.minutes,
        "servings": r.servings,
        "meal": r.meal,
        "meal_name": MEAL_NAMES.get(r.meal, r.meal),
        "tags": r.tags,
        "kcal": round(r.kcal),
        "protein": round(r.protein),
        "fat": round(r.fat),
        "carbs": round(r.carbs),
        "verified": r.verified,
    }


# --- цель ----------------------------------------------------------------------------------


def _goal_state(db: Session, user: User) -> dict[str, Any]:
    profile = _profile(db, user)
    saved = _saved_goal(db, user)
    mode = saved.mode if saved else "maintain"
    adjust = saved.adjust_kcal if saved else 0
    flags = list(saved.restrictions) if saved else []
    blocked = calc.blocks_for(profile, flags)
    current = calc.compute(profile, mode, adjust, flags)
    options = {}
    for key in calc.MODES:
        option = calc.compute(profile, key, adjust, flags)
        options[key] = option.kcal if option else None
    names = {**calc.SCREENING, **calc.AUTO_BLOCKS}
    return {
        "profile": {
            "weight_kg": profile.weight_kg,
            "height_cm": profile.height_cm,
            "age": profile.age,
            "sex": profile.sex,
            "lifestyle": profile.lifestyle,
        },
        "complete": current is not None,
        "requested_mode": mode,
        "adjust_kcal": adjust,
        "restrictions": flags,
        "blocked": [{"key": b, "name": names[b]} for b in blocked],
        "lose_blocked": bool(blocked),
        "screening": [{"key": k, "name": v} for k, v in calc.SCREENING.items()],
        "goal": _goal_dict(current),
        "options": options,
        "trend_hint": _trend_hint(db, user) if mode == "lose" else None,
        "disclaimer": (
            "Это ориентир, а не медицинская рекомендация. "
            "При заболеваниях и особых состояниях обратитесь к врачу или диетологу."
        ),
    }


@router.get("/nutrition/goal")
def get_goal(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    return _goal_state(db, user)


@router.put("/nutrition/goal")
def put_goal(
    body: GoalIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    if any(flag not in calc.SCREENING for flag in body.restrictions):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "unknown restriction")
    flags = sorted(set(body.restrictions))
    if body.mode == "lose" and calc.blocks_for(_profile(db, user), flags):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "lose_blocked")
    row = _saved_goal(db, user) or NutritionGoal(user_id=user.id)
    row.mode = body.mode
    row.adjust_kcal = calc.clamp_adjust(body.adjust_kcal)
    row.restrictions = flags
    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    return _goal_state(db, user)


# --- дневник -------------------------------------------------------------------------------


def _day_state(db: Session, user: User, day: dt.date) -> dict[str, Any]:
    entries = list(
        db.scalars(
            select(FoodEntry)
            .where(FoodEntry.user_id == user.id, FoodEntry.date == day)
            .order_by(FoodEntry.id)
        )
    )
    totals = _sum(entries)
    state = _goal_state(db, user)
    goal = state["goal"]
    remaining = None
    hints: list[str] = []
    if goal:
        remaining = {
            "kcal": goal["kcal"] - totals["kcal"],
            "protein": round(goal["protein_g"] - totals["protein"], 1),
            "fat": round(goal["fat_g"] - totals["fat"], 1),
            "carbs": round(goal["carbs_g"] - totals["carbs"], 1),
        }
        if remaining["protein"] >= 10:
            hints.append(f"Белка не хватает {round(remaining['protein'])} г.")
        if remaining["kcal"] < 0:
            hints.append(f"Выше цели на {-round(remaining['kcal'])} ккал. Завтра новый день.")
    meals = [
        {
            "meal": meal,
            "name": MEAL_NAMES[meal],
            "entries": [_entry_dict(e) for e in entries if e.meal == meal],
            "totals": _sum([e for e in entries if e.meal == meal]),
        }
        for meal in MEALS
    ]
    return {
        "date": day.isoformat(),
        "goal": goal,
        "mode": state["requested_mode"],
        "complete": state["complete"],
        "totals": totals,
        "remaining": remaining,
        "hints": hints,
        "meals": meals,
    }


@router.get("/nutrition/day")
def get_day(
    date_: dt.date | None = Query(default=None, alias="date"),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return _day_state(db, user, _day(date_))


def _entry_values(
    db: Session, user: User, body: EntryIn | None, entry: FoodEntry | None, patch: EntryPatch | None
) -> dict[str, Any]:
    """КБЖУ записи по продукту (граммы) или рецепту (порции)."""
    food_id = body.food_id if body else (entry.food_id if entry else None)
    recipe_id = body.recipe_id if body else (entry.recipe_id if entry else None)
    if (food_id is None) == (recipe_id is None):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "food_id or recipe_id")
    if food_id is not None:
        grams = (patch.grams if patch else None) or (body.grams if body else None)
        grams = grams or (entry.grams if entry else None)
        if grams is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "grams required")
        food = LocalFoodSource(db, user.id).get(food_id)
        if food is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "food not found")
        k = grams / 100
        return {
            "food_id": food.id,
            "recipe_id": None,
            "name": food.name,
            "grams": grams,
            "servings": None,
            "kcal": food.kcal * k,
            "protein": food.protein * k,
            "fat": food.fat * k,
            "carbs": food.carbs * k,
        }
    servings = (patch.servings if patch else None) or (body.servings if body else None)
    servings = servings or (entry.servings if entry else None) or 1.0
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "recipe not found")
    return {
        "food_id": None,
        "recipe_id": recipe.id,
        "name": recipe.name,
        "grams": None,
        "servings": servings,
        "kcal": recipe.kcal * servings,
        "protein": recipe.protein * servings,
        "fat": recipe.fat * servings,
        "carbs": recipe.carbs * servings,
    }


@router.post("/nutrition/entries", status_code=status.HTTP_201_CREATED)
def add_entry(
    body: EntryIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    day = _day(body.date)
    values = _entry_values(db, user, body, None, None)
    entry = FoodEntry(user_id=user.id, date=day, meal=body.meal, **values)
    db.add(entry)
    db.commit()
    return _entry_dict(entry)


def _own_entry(db: Session, user: User, entry_id: int) -> FoodEntry:
    entry = db.get(FoodEntry, entry_id)
    if entry is None or entry.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "entry not found")
    return entry


@router.patch("/nutrition/entries/{entry_id}")
def patch_entry(
    entry_id: int,
    body: EntryPatch,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    entry = _own_entry(db, user, entry_id)
    values = _entry_values(db, user, None, entry, body)
    for key, value in values.items():
        setattr(entry, key, value)
    if body.meal:
        entry.meal = body.meal
    db.commit()
    return _entry_dict(entry)


@router.delete("/nutrition/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> None:
    db.delete(_own_entry(db, user, entry_id))
    db.commit()


# --- продукты ------------------------------------------------------------------------------


@router.get("/nutrition/foods")
def search_foods(
    q: str = Query(default="", max_length=60),
    group: str | None = Query(default=None, max_length=16),
    limit: int = Query(default=30, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    found = LocalFoodSource(db, user.id).search(q, limit, group)
    return {
        "items": [_food_dict(f) for f in found],
        "groups": [{"key": k, "name": v} for k, v in FOOD_GROUPS.items()],
    }


@router.get("/nutrition/foods/recent")
def recent_foods(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Часто добавляемые и недавние продукты с последней граммовкой."""
    since = utcnow().date() - timedelta(days=60)
    rows = db.execute(
        select(FoodEntry.food_id, func.count(), func.max(FoodEntry.id))
        .where(
            FoodEntry.user_id == user.id, FoodEntry.date >= since, FoodEntry.food_id.is_not(None)
        )
        .group_by(FoodEntry.food_id)
    ).all()
    source = LocalFoodSource(db, user.id)

    def build(food_id: int, last_entry: int) -> dict[str, Any] | None:
        food = source.get(food_id)
        entry = db.get(FoodEntry, last_entry)
        if food is None or entry is None:
            return None
        return {**_food_dict(food), "last_grams": entry.grams}

    frequent = sorted(rows, key=lambda r: (-r[1], -r[2]))[:8]
    recent = sorted(rows, key=lambda r: -r[2])[:8]
    return {
        "frequent": [x for x in (build(r[0], r[2]) for r in frequent) if x],
        "recent": [x for x in (build(r[0], r[2]) for r in recent) if x],
    }


@router.post("/nutrition/foods", status_code=status.HTTP_201_CREATED)
def create_food(
    body: FoodIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Личный продукт: виден только автору, в общую базу не попадает."""
    if body.protein + body.fat + body.carbs > 100.5:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "macros exceed 100 g")
    count = db.scalar(select(func.count()).select_from(Food).where(Food.owner_id == user.id))
    if (count or 0) >= 200:
        raise HTTPException(status.HTTP_409_CONFLICT, "too many own foods")
    food = Food(
        name=body.name.strip(),
        group="other",
        kcal=body.kcal,
        protein=body.protein,
        fat=body.fat,
        carbs=body.carbs,
        owner_id=user.id,
        verified=False,
        source="user",
    )
    db.add(food)
    db.commit()
    return _food_dict(food)


# --- рецепты -------------------------------------------------------------------------------


def _all_recipes(db: Session) -> list[Recipe]:
    return list(db.scalars(select(Recipe).order_by(Recipe.name)))


@router.get("/nutrition/recipes")
def list_recipes(
    tag: str | None = Query(default=None, max_length=16),
    meal: str | None = Query(default=None, max_length=10),
    q: str = Query(default="", max_length=60),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    items = _all_recipes(db)
    needle = q.strip().casefold()
    items = [
        r
        for r in items
        if (not tag or tag in r.tags)
        and (not meal or r.meal == meal)
        and (not needle or needle in r.name.casefold())
    ]
    return {
        "items": [_recipe_card(r) for r in items],
        "tags": [{"key": k, "name": v} for k, v in TAG_NAMES.items()],
        "total": len(items),
    }


@router.get("/nutrition/recipes/suggest")
def suggest_recipes(
    training: Literal["before", "after"] | None = Query(default=None),
    direction: str | None = Query(default=None, max_length=16),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Подбор под остаток дня, время тренировки и направление; у каждого рецепта своя причина."""
    day = _day_state(db, user, utcnow().date())
    remaining = day["remaining"]
    left_kcal = remaining["kcal"] if remaining else None
    left_protein = remaining["protein"] if remaining else None
    cards = [_recipe_card(r) for r in _all_recipes(db)]
    picked = suggest(
        cards, left_kcal, left_protein, training, training == "after" and direction == "running"
    )
    summary = None
    if remaining:
        summary = f"Осталось {max(0, round(remaining['kcal']))} ккал"
        if remaining["protein"] >= 10:
            summary += f", белка не хватает {round(remaining['protein'])} г"
        summary += "."
    return {"summary": summary, "items": picked}


@router.get("/nutrition/recipes/{recipe_id}")
def get_recipe(
    recipe_id: int,
    servings: float = Query(default=1, ge=0.25, le=12),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "recipe not found")
    foods = {f.slug: f for f in db.scalars(select(Food).where(Food.slug.is_not(None)))}
    factor = servings / recipe.servings
    ingredients = []
    for item in recipe.ingredients:
        food = foods.get(item["food"])
        grams = item["grams"] * factor
        ingredients.append(
            {
                "name": food.name if food else item["food"],
                "grams": round(grams / 5) * 5 if grams >= 20 else round(grams, 1),
            }
        )
    return {
        **_recipe_card(recipe),
        "servings_shown": servings,
        "per_serving": {
            "kcal": round(recipe.kcal),
            "protein": round(recipe.protein, 1),
            "fat": round(recipe.fat, 1),
            "carbs": round(recipe.carbs, 1),
        },
        "ingredients": ingredients,
        "steps": recipe.steps,
        "note": "Значения приблизительные: рассчитаны по ингредиентам, продукты не проверены.",
    }
