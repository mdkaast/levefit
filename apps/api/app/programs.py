"""Каталог и программы для пользователя: профиль → шаблон → упражнения в слотах."""

from datetime import timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.content import resolver
from app.content.matrix import recommend
from app.content.muscles import PATTERN_NAMES
from app.game import utcnow
from app.models import (
    Exercise,
    ExerciseMuscle,
    Muscle,
    ProgramTemplate,
    TemplateMatrix,
    User,
    Workout,
)

GOAL_ALIASES = {"shape": "general"}
EQUIPMENT_PROFILE = {"gym": "gym", "home": "dumbbells", "none": "bodyweight"}
BREAK_DAYS = 14  # перерыв от двух недель: сначала возвращение (T14)
SCENARIOS = {"noBB", "DB", "BW", "KNEE", "LB", "SH", "EL"}


def exercise_dict(e: Exercise) -> dict[str, Any]:
    return {
        "id": e.id,
        "slug": e.slug,
        "name": e.name,
        "pattern": e.pattern,
        "category": e.category,
        "level": e.level or "beginner",
        "equipment": e.equipment or [["bodyweight"]],
        "caution_flags": e.caution_flags or [],
        "ui_groups": e.ui_groups or [],
        "subs": e.subs or {},
        "variant_of": e.variant_of,
        "load_type": e.load_type,
        "is_active": e.is_active,
    }


def load_catalog(db: Session) -> dict[str, dict[str, Any]]:
    """Активные упражнения каталога по slug (пользовательские и прежние без slug сюда не входят)."""
    rows = db.scalars(
        select(Exercise).where(Exercise.slug.is_not(None), Exercise.is_active.is_(True))
    )
    return {e.slug: exercise_dict(e) for e in rows}


def profile_of(user: User) -> dict[str, Any]:
    """Ответы онбординга в терминах матрицы."""
    character = user.character
    goal = (character.goal if character else None) or "general"
    equipment = (character.equipment if character else None) or "gym"
    return {
        "goal": GOAL_ALIASES.get(goal, goal),
        "days": min(6, max(2, character.workouts_per_week if character else 3)),
        "level": (character.experience if character else None) or "beginner",
        "inventory": EQUIPMENT_PROFILE.get(equipment, "gym"),
        "age": character.age if character else None,
    }


def conditions_for(db: Session, user: User, age: int | None) -> set[str]:
    found: set[str] = set()
    if age is not None and age >= 50:
        found.add("age50")
    last = db.scalar(
        select(func.max(Workout.date)).where(
            Workout.user_id == user.id, Workout.status == "finished"
        )
    )
    if last is not None and (utcnow().date() - last) > timedelta(days=BREAK_DAYS):
        found.add("break")
    return found


def matrix_rows(db: Session) -> list[dict[str, Any]]:
    return [
        {
            "goal": r.goal,
            "days": r.days,
            "level": r.level,
            "inventory": r.inventory,
            "condition": r.condition,
            "mode": r.mode,
            "templates": r.templates,
            "note": r.note,
        }
        for r in db.scalars(select(TemplateMatrix))
    ]


def recommend_for(
    db: Session,
    user: User,
    overrides: dict[str, Any] | None = None,
    conditions: set[str] | None = None,
) -> dict[str, Any] | None:
    """Рекомендация шаблона по профилю; None, если матрица в БД ещё не загружена."""
    rows = matrix_rows(db)
    if not rows:
        return None
    profile = {**profile_of(user), **(overrides or {})}
    if profile["goal"] not in {r["goal"] for r in rows if r["goal"]}:
        profile["goal"] = "general"
    active = conditions if conditions is not None else conditions_for(db, user, profile["age"])
    result = recommend(
        rows, profile["goal"], profile["days"], profile["level"], profile["inventory"], active
    )
    return {**result, "profile": profile, "conditions": sorted(active)}


def usable_template(db: Session, template_id: str) -> tuple[str, str | None]:
    """Шаблон, который движок умеет вести. Если нет, берётся запасной с двойной прогрессией."""
    row = db.get(ProgramTemplate, template_id)
    if row is None or row.engine_ready or not row.fallback:
        return template_id, None
    return (
        row.fallback,
        f"Прогрессия шаблона {template_id} пока не поддерживается, ведём как {row.fallback}.",
    )


def resolve_for_user(
    db: Session,
    template_id: str,
    profile: dict[str, Any],
    zones: set[str] | None = None,
) -> dict[str, Any]:
    """Дни шаблона с упражнениями под инвентарь, уровень и жалобы; составные раскрываются."""
    row = db.get(ProgramTemplate, template_id)
    if row is None:
        raise KeyError(template_id)
    spec = row.spec
    base_id = None
    if spec.get("base_by_days"):
        inventory = profile["inventory"]
        base_id = (
            spec.get("base_home", {}).get(inventory) or spec["base_by_days"][str(profile["days"])]
        )
        spec_for_days = db.get(ProgramTemplate, base_id).spec
    else:
        spec_for_days = spec
    inventory_items = resolver.inventory_items(profile["inventory"])
    flags = resolver.blocked_flags(zones or set())
    resolved = resolver.resolve_template(
        spec_for_days, load_catalog(db), inventory_items, profile["level"], flags
    )
    return {"template": row, "spec": spec, "base_id": base_id, "resolved": resolved}


def volume_by_group(db: Session, slugs_sets: list[tuple[str, float]]) -> list[dict[str, Any]]:
    """Подходы по группам мышц за цикл шаблона: подходы × вклад мышцы (1,0 и 0,5)."""
    if not slugs_sets:
        return []
    ids = {
        e.slug: e.id
        for e in db.scalars(select(Exercise).where(Exercise.slug.in_([s for s, _ in slugs_sets])))
    }
    links = db.execute(
        select(ExerciseMuscle.exercise_id, Muscle.ui_group, ExerciseMuscle.volume_weight)
        .join(Muscle, Muscle.id == ExerciseMuscle.muscle_id)
        .where(ExerciseMuscle.exercise_id.in_(list(ids.values())))
    ).all()
    by_exercise: dict[int, list[tuple[str, float]]] = {}
    for exercise_id, group, weight in links:
        by_exercise.setdefault(exercise_id, []).append((group, weight))
    totals: dict[str, float] = {}
    for slug, sets in slugs_sets:
        for group, weight in by_exercise.get(ids.get(slug, -1), []):
            totals[group] = totals.get(group, 0.0) + sets * weight
    return [
        {"group": g, "sets": round(v, 1)}
        for g, v in sorted(totals.items(), key=lambda item: -item[1])
    ]


def substitutes(
    db: Session,
    exercise: Exercise,
    inventory: set[str] | None,
    level: str,
    zones: set[str],
    scenario: str | None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Замены: явные из каталога → то же семейство → тот же паттерн с общими мышцами."""
    catalog = load_catalog(db)
    me = exercise_dict(exercise)
    flags = resolver.blocked_flags(zones)
    explicit = (
        (me["subs"] or {}).get(scenario, [])
        if scenario
        else [s for v in me["subs"].values() for s in v]
    )
    family = {
        slug
        for slug, e in catalog.items()
        if slug != me["slug"]
        and (
            e["variant_of"] == me["slug"]
            or (me["variant_of"] and slug == me["variant_of"])
            or (me["variant_of"] and e["variant_of"] == me["variant_of"])
        )
    }
    scored: dict[str, tuple[tuple, str]] = {}

    def consider(slug: str, rank: tuple, reason: str) -> None:
        e = catalog.get(slug)
        if e is None or slug == me["slug"]:
            return
        if inventory is not None and not resolver.available(e, inventory):
            return
        if resolver.excluded(e, flags) or not resolver.level_ok(e, level) and reason == "pattern":
            return
        if slug not in scored or rank < scored[slug][0]:
            scored[slug] = (rank, reason)

    for index, slug in enumerate(explicit):
        consider(slug, (0, index), "explicit")
    for slug in sorted(family):
        consider(slug, (1, 0), "family")
    mine = set(me["ui_groups"])
    for slug, e in catalog.items():
        if e["pattern"] == me["pattern"] and e["category"] == me["category"]:
            overlap = len(mine & set(e["ui_groups"]))
            if overlap:
                consider(slug, (2, -overlap, resolver.LEVELS.index(e["level"]), slug), "pattern")
    ordered = sorted(scored.items(), key=lambda item: item[1][0])[:limit]
    return [
        {"id": catalog[slug]["id"], "slug": slug, "name": catalog[slug]["name"], "reason": reason}
        for slug, (_, reason) in ordered
    ]


def pattern_name(pattern: str | None) -> str:
    return PATTERN_NAMES.get(pattern or "", pattern or "")
