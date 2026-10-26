"""Загрузка продуктов и рецептов в БД. Идемпотентна: обновляет по slug, ничего не удаляет."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content.foods_data import FOODS
from app.content.recipes_data import RECIPES
from app.models import Food, Recipe
from app.nutrition_recipes import auto_tags, macros


def seed_nutrition(db: Session) -> dict[str, int]:
    stats = {"foods": 0, "recipes": 0}
    foods = {f.slug: f for f in db.scalars(select(Food).where(Food.slug.is_not(None)))}
    for slug, name, group, kcal, protein, fat, carbs, piece_g, piece_name in FOODS:
        row = foods.get(slug)
        if row is None:
            row = Food(slug=slug, verified=False, source="estimate")
            db.add(row)
            foods[slug] = row
        row.name, row.group = name, group
        row.kcal, row.protein, row.fat, row.carbs = kcal, protein, fat, carbs
        row.piece_g, row.piece_name = piece_g, piece_name
        stats["foods"] += 1
    db.flush()

    by_slug = {slug: foods[slug] for slug in foods}
    existing = {r.slug: r for r in db.scalars(select(Recipe))}
    for slug, name, minutes, servings, meal, items, steps in RECIPES:
        per100 = [
            (
                {
                    "kcal": by_slug[f].kcal,
                    "protein": by_slug[f].protein,
                    "fat": by_slug[f].fat,
                    "carbs": by_slug[f].carbs,
                },
                grams,
            )
            for f, grams in items
        ]
        per_serving = macros(per100, servings)
        tags = auto_tags(per_serving, minutes, {by_slug[f].group for f, _ in items})
        row = existing.get(slug)
        if row is None:
            row = Recipe(slug=slug, verified=False, source="own")
            db.add(row)
        row.name, row.minutes, row.servings, row.meal = name, minutes, servings, meal
        row.tags = tags
        row.ingredients = [{"food": f, "grams": g} for f, g in items]
        row.steps = [s.strip() for s in steps.split("|")]
        row.kcal, row.protein = per_serving["kcal"], per_serving["protein"]
        row.fat, row.carbs = per_serving["fat"], per_serving["carbs"]
        stats["recipes"] += 1
    db.commit()
    return stats
