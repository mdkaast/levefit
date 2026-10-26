"""КБЖУ рецептов, автоматические теги и подбор по остатку дня (F5, F6). Чистые функции."""

from typing import Any

NON_VEGETARIAN_GROUPS = {"meat", "fish", "ready"}

TAG_NAMES = {
    "protein": "Белок",
    "quick": "Быстро",
    "light": "Лёгкое",
    "pre": "До тренировки",
    "post": "После тренировки",
    "post_run": "После бега",
    "vegetarian": "Без мяса и рыбы",
}
MEAL_NAMES = {"breakfast": "Завтрак", "lunch": "Обед", "dinner": "Ужин", "snack": "Перекус"}

QUICK_MINUTES = 20
LIGHT_KCAL = 400


def macros(ingredients: list[tuple[dict[str, float], float]], servings: int) -> dict[str, float]:
    """КБЖУ на порцию: ингредиенты (продукт на 100 г, граммы на весь рецепт)."""
    total = {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}
    for food, grams in ingredients:
        for key in total:
            total[key] += food[key] * grams / 100
    return {key: round(value / servings, 1) for key, value in total.items()}


def auto_tags(per_serving: dict[str, float], minutes: int, groups: set[str]) -> list[str]:
    kcal, protein = per_serving["kcal"], per_serving["protein"]
    fat, carbs = per_serving["fat"], per_serving["carbs"]
    tags: list[str] = []
    if protein >= 30 or (protein >= 20 and protein * 4 / max(kcal, 1) >= 0.30):
        tags.append("protein")
    if minutes <= QUICK_MINUTES:
        tags.append("quick")
    if kcal <= LIGHT_KCAL:
        tags.append("light")
    if fat <= 12 and carbs >= 35 and kcal <= 500:
        tags.append("pre")
    if protein >= 25 and carbs >= 20:
        tags.append("post")
    if protein >= 20 and carbs >= 45:
        tags.append("post_run")
    if not (groups & NON_VEGETARIAN_GROUPS):
        tags.append("vegetarian")
    return tags


def suggest(
    recipes: list[dict[str, Any]],
    remaining_kcal: float | None,
    remaining_protein: float | None,
    training: str | None,
    after_run: bool,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Подбор на правилах: что влезает в остаток дня, закрывает белок и подходит к тренировке.

    Каждой карточке возвращается причина простыми словами («подходит, так как…»).
    """
    scored: list[tuple[float, dict[str, Any]]] = []
    kcal_left = remaining_kcal if remaining_kcal is not None else 700
    protein_left = max(0.0, remaining_protein) if remaining_protein is not None else 30
    target = min(max(kcal_left, 0), max(250.0, kcal_left / 2))
    for recipe in recipes:
        if kcal_left > 0 and recipe["kcal"] > kcal_left * 1.15 + 50:
            continue
        reasons: list[str] = []
        score = 0.0
        fit = 1 - min(1.0, abs(recipe["kcal"] - target) / max(target, 1))
        score += fit
        if kcal_left > 0 and recipe["kcal"] <= kcal_left:
            reasons.append(f"помещается в остаток дня ({round(kcal_left)} ккал)")
        covered = min(recipe["protein"], protein_left)
        if protein_left >= 10 and covered >= 15:
            share = round(covered / protein_left * 100)
            reasons.append(f"закрывает около {share}% недостающего белка")
            score += 2 * covered / protein_left
        tags = recipe["tags"]
        if after_run and "post_run" in tags:
            reasons.append("после бега: углеводы и белок")
            score += 1.5
        elif training == "before" and "pre" in tags:
            reasons.append("перед тренировкой: мало жира и есть углеводы")
            score += 1.5
        elif training == "after" and "post" in tags:
            reasons.append("после тренировки: достаточно белка и углеводов")
            score += 1.5
        if not reasons:
            reasons.append("по калорийности близко к вашему приёму пищи")
        scored.append(
            (score, {**recipe, "reason": "Подходит, так как " + "; ".join(reasons) + "."})
        )
    scored.sort(key=lambda item: (-item[0], item[1]["name"]))
    return [item for _, item in scored[:limit]]
