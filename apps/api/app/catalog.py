"""Каталог упражнений и программ: поиск, карточка, замены, шаблоны и подбор под профиль."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import programs
from app.content import resolver
from app.content.muscles import (
    EQUIPMENT_NAMES,
    FLAG_NAMES,
    LEVEL_NAMES,
    UI_GROUPS,
)
from app.db import get_db
from app.deps import current_user
from app.models import Exercise, ExerciseMuscle, Muscle, ProgramTemplate, User

router = APIRouter()

INVENTORY_KEYS = "gym|home_barbell|dumbbells|bodyweight|kettlebell"
LEVEL_KEYS = "beginner|intermediate|advanced"


class GroupOut(BaseModel):
    key: str
    name: str
    count: int


class ExerciseItem(BaseModel):
    id: int
    slug: str | None
    name: str
    pattern: str | None
    pattern_name: str
    level: str | None
    level_name: str | None
    ui_groups: list[str]
    primary_muscles: list[str]
    fits_you: bool
    verified: bool


class ExerciseList(BaseModel):
    total: int  # найдено по фильтру
    catalog_total: int  # всего активных упражнений каталога («из 374»)
    items: list[ExerciseItem]


class MuscleOut(BaseModel):
    slug: str
    name: str
    ui_group: str
    role: str
    volume_weight: float


class SubstituteOut(BaseModel):
    id: int
    slug: str
    name: str
    reason: str


class ExerciseCard(ExerciseItem):
    name_en: str | None
    category: str
    equipment: list[list[str]]
    equipment_names: list[list[str]]
    load_type: str | None
    load_increment_kg: float | None
    e1rm: str | None
    flags: list[str]
    muscles: list[MuscleOut]
    aliases: list[str]
    cues: list[str]  # подсказки по технике: в каталоге их нет, поле заложено под медиа и тексты
    media: list[str]
    substitutes: list[SubstituteOut]


class SlotOut(BaseModel):
    pattern: str
    pattern_name: str
    role: str
    sets: list[int]
    reps: list[int]
    rir: list[int] | None
    progression: str
    exercise_id: int | None
    exercise_slug: str | None
    exercise_name: str | None
    via: str
    note: str | None = None


class DayOut(BaseModel):
    name: str
    slots: list[SlotOut]


class ProgramCard(BaseModel):
    id: str
    name: str
    summary: str
    days_min: int
    days_max: int
    session: list[int]
    progression: str
    engine_ready: bool
    fallback: str | None
    verified: bool
    fits_you: bool
    goals: list[str]
    levels: list[str]
    inventory: list[str]
    on_request_only: bool = False


class VolumeOut(BaseModel):
    group: str
    name: str
    sets: float


class ProgramDetail(ProgramCard):
    principle: str
    warning: str | None
    rules: dict[str, Any] | None
    phases: list[dict[str, Any]] | None
    stages: dict[str, Any] | None
    week_scheme: list[Any] | None
    cardio: dict[str, Any] | None
    base_template: str | None
    days: list[DayOut]
    volume: list[VolumeOut]
    empty_slots: list[str]
    inventory_used: str
    level_used: str


class Recommendation(BaseModel):
    primary: ProgramCard
    then: list[ProgramCard]
    reasons: list[str]
    usable_id: str
    usable_note: str | None
    inputs: dict[str, Any]


def _fits(exercise: Exercise, inventory: set[str], level: str) -> bool:
    data = programs.exercise_dict(exercise)
    return resolver.available(data, inventory) and resolver.level_ok(data, level)


def _item(e: Exercise, primary: list[str], inventory: set[str], level: str) -> ExerciseItem:
    return ExerciseItem(
        id=e.id,
        slug=e.slug,
        name=e.name,
        pattern=e.pattern,
        pattern_name=programs.pattern_name(e.pattern),
        level=e.level,
        level_name=LEVEL_NAMES.get(e.level or ""),
        ui_groups=e.ui_groups or [],
        primary_muscles=primary,
        fits_you=_fits(e, inventory, level) if e.slug else True,
        verified=e.verified,
    )


def _primary_muscles(db: Session, ids: list[int]) -> dict[int, list[str]]:
    rows = db.execute(
        select(ExerciseMuscle.exercise_id, Muscle.name_ru)
        .join(Muscle, Muscle.id == ExerciseMuscle.muscle_id)
        .where(ExerciseMuscle.exercise_id.in_(ids), ExerciseMuscle.role == "primary")
    )
    result: dict[int, list[str]] = {}
    for exercise_id, name in rows:
        result.setdefault(exercise_id, []).append(name)
    return result


def _user_context(user: User) -> tuple[set[str], str]:
    profile = programs.profile_of(user)
    return resolver.inventory_items(profile["inventory"]), profile["level"]


@router.get("/catalog/groups", response_model=list[GroupOut])
def groups(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[GroupOut]:
    counts: dict[str, int] = {}
    for ui_groups in db.scalars(
        select(Exercise.ui_groups).where(Exercise.is_active.is_(True), Exercise.slug.is_not(None))
    ):
        for key in ui_groups or []:
            counts[key] = counts.get(key, 0) + 1
    return [
        GroupOut(key=k, name=name, count=counts.get(k, 0))
        for k, name in UI_GROUPS.items()
        if counts.get(k)
    ]


@router.get("/catalog/exercises", response_model=ExerciseList)
def search_exercises(
    q: str | None = Query(default=None, max_length=60),
    group: str | None = None,
    pattern: str | None = None,
    level: str | None = Query(default=None, pattern=f"^({LEVEL_KEYS})$"),
    fits: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> ExerciseList:
    inventory, user_level = _user_context(user)
    base = select(Exercise).where(Exercise.is_active.is_(True), Exercise.slug.is_not(None))
    total_catalog = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    query = base
    if pattern:
        query = query.where(Exercise.pattern == pattern)
    if level:
        query = query.where(Exercise.level == level)
    rows = list(db.scalars(query.order_by(Exercise.name)))
    if q:  # регистр сравниваем в Python: SQLite не понижает регистр кириллицы
        needle = q.strip().casefold()
        rows = [
            e
            for e in rows
            if needle in e.name.casefold()
            or needle in (e.name_en or "").casefold()
            or needle in (e.slug or "")
        ]
    if group:
        rows = [e for e in rows if group in (e.ui_groups or [])]
    if fits:
        rows = [e for e in rows if _fits(e, inventory, user_level)]
    total = len(rows)
    page = rows[offset : offset + limit]
    primary = _primary_muscles(db, [e.id for e in page]) if page else {}
    return ExerciseList(
        total=total,
        catalog_total=total_catalog,
        items=[_item(e, primary.get(e.id, []), inventory, user_level) for e in page],
    )


@router.get("/catalog/exercises/{exercise_id}", response_model=ExerciseCard)
def exercise_card(
    exercise_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> ExerciseCard:
    e = db.get(Exercise, exercise_id)
    if e is None or e.owner_id not in (None, user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "exercise not found")
    inventory, level = _user_context(user)
    links = db.execute(
        select(Muscle, ExerciseMuscle)
        .join(ExerciseMuscle, ExerciseMuscle.muscle_id == Muscle.id)
        .where(ExerciseMuscle.exercise_id == e.id)
        .order_by(ExerciseMuscle.volume_weight.desc(), Muscle.name_ru)
    ).all()
    muscles = [
        MuscleOut(
            slug=m.slug,
            name=m.name_ru,
            ui_group=m.ui_group,
            role=link.role,
            volume_weight=link.volume_weight,
        )
        for m, link in links
    ]
    primary = [m.name for m in muscles if m.role == "primary"]
    base = _item(e, primary, inventory, level)
    subs = programs.substitutes(db, e, inventory, level, set(), None) if e.slug else []
    return ExerciseCard(
        **base.model_dump(),
        name_en=e.name_en,
        category=e.category,
        equipment=e.equipment or [],
        equipment_names=[[EQUIPMENT_NAMES.get(i, i) for i in alt] for alt in (e.equipment or [])],
        load_type=e.load_type,
        load_increment_kg=e.load_increment_kg,
        e1rm=e.e1rm,
        flags=[FLAG_NAMES.get(f, f) for f in (e.caution_flags or [])],
        muscles=muscles,
        aliases=e.aliases or [],
        cues=[],
        media=[],
        substitutes=[SubstituteOut(**s) for s in subs],
    )


@router.get("/catalog/exercises/{exercise_id}/substitutes", response_model=list[SubstituteOut])
def exercise_substitutes(
    exercise_id: int,
    scenario: str | None = Query(default=None, pattern="^(noBB|DB|BW|KNEE|LB|SH|EL)$"),
    inventory: str | None = Query(default=None, pattern=f"^({INVENTORY_KEYS})$"),
    zones: list[str] = Query(default=[]),
    limit: int = Query(default=8, ge=1, le=20),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[SubstituteOut]:
    """Замена: по сценарию (нет штанги, колено, поясница), инвентарю и жалобам на зоны."""
    e = db.get(Exercise, exercise_id)
    if e is None or e.owner_id not in (None, user.id) or not e.slug:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "exercise not found")
    profile = programs.profile_of(user)
    items = resolver.inventory_items(inventory or profile["inventory"])
    found = programs.substitutes(db, e, items, profile["level"], set(zones), scenario, limit)
    return [SubstituteOut(**s) for s in found]


def _card(t: ProgramTemplate, profile: dict[str, Any], recommended: set[str]) -> ProgramCard:
    return ProgramCard(
        id=t.id,
        name=t.name,
        summary=t.summary,
        days_min=t.days_min,
        days_max=t.days_max,
        session=t.spec["session"],
        progression=t.progression,
        engine_ready=t.engine_ready,
        fallback=t.fallback,
        verified=t.verified,
        fits_you=t.id in recommended,
        goals=t.goals,
        levels=t.levels,
        inventory=t.inventory,
        on_request_only=bool(t.spec.get("on_request_only")),
    )


@router.get("/programs", response_model=list[ProgramCard])
def list_programs(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[ProgramCard]:
    profile = programs.profile_of(user)
    rec = programs.recommend_for(db, user)
    recommended = {rec["primary"], *rec["then"]} if rec else set()
    rows = list(db.scalars(select(ProgramTemplate).order_by(ProgramTemplate.id)))
    cards = [_card(t, profile, recommended) for t in rows]
    return sorted(cards, key=lambda c: (not c.fits_you, c.id))


@router.get("/programs/recommend", response_model=Recommendation)
def recommend_program(
    goal: str | None = Query(
        default=None, pattern="^(strength|strength_mass|mass|return|weight_loss|general)$"
    ),
    days: int | None = Query(default=None, ge=2, le=6),
    level: str | None = Query(default=None, pattern=f"^({LEVEL_KEYS})$"),
    inventory: str | None = Query(default=None, pattern=f"^({INVENTORY_KEYS})$"),
    short: bool = False,
    split: bool = False,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Recommendation:
    """Шаблон по ответам онбординга: любой ответ даёт программу без пустых слотов."""
    overrides = {
        k: v
        for k, v in {"goal": goal, "days": days, "level": level, "inventory": inventory}.items()
        if v
    }
    profile = {**programs.profile_of(user), **overrides}
    conditions = programs.conditions_for(db, user, profile["age"])
    if short:
        conditions.add("short30")
    if split:
        conditions.add("split")
    rec = programs.recommend_for(db, user, overrides, conditions)
    if rec is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "catalog is not loaded")
    ids = [rec["primary"], *rec["then"]]
    by_id = {
        t.id: t for t in db.scalars(select(ProgramTemplate).where(ProgramTemplate.id.in_(ids)))
    }
    usable, note = programs.usable_template(db, rec["primary"])
    return Recommendation(
        primary=_card(by_id[rec["primary"]], profile, {rec["primary"]}),
        then=[_card(by_id[i], profile, {i}) for i in rec["then"]],
        reasons=rec["reasons"],
        usable_id=usable,
        usable_note=note,
        inputs={**rec["profile"], "conditions": rec["conditions"]},
    )


@router.get("/programs/{template_id}", response_model=ProgramDetail)
def program_detail(
    template_id: str,
    inventory: str | None = Query(default=None, pattern=f"^({INVENTORY_KEYS})$"),
    level: str | None = Query(default=None, pattern=f"^({LEVEL_KEYS})$"),
    days: int | None = Query(default=None, ge=2, le=6),
    zones: list[str] = Query(default=[]),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> ProgramDetail:
    profile = {
        **programs.profile_of(user),
        **{k: v for k, v in {"inventory": inventory, "level": level, "days": days}.items() if v},
    }
    row = db.get(ProgramTemplate, template_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "program not found")
    result = programs.resolve_for_user(db, template_id, profile, set(zones))
    spec = result["spec"]
    rec = programs.recommend_for(db, user)
    recommended = {rec["primary"], *rec["then"]} if rec else set()

    ids = {
        e.slug: e
        for e in db.scalars(
            select(Exercise).where(
                Exercise.slug.in_(
                    [s["slug"] for d in result["resolved"]["days"] for s in d["slots"] if s["slug"]]
                )
            )
        )
    }
    days_out: list[DayOut] = []
    volume_input: list[tuple[str, float]] = []
    for day in result["resolved"]["days"]:
        slots = []
        for item in day["slots"]:
            slot, slug = item["slot"], item["slug"]
            exercise = ids.get(slug) if slug else None
            if (
                exercise
                and exercise.category == "strength"
                and slot["progression"] not in ("time", "warmup")
            ):
                volume_input.append((slug, float(slot["sets"][1])))
            slots.append(
                SlotOut(
                    pattern=slot["pattern"],
                    pattern_name=programs.pattern_name(slot["pattern"]),
                    role=slot["role"],
                    sets=slot["sets"],
                    reps=slot["reps"],
                    rir=slot.get("rir"),
                    progression=slot["progression"],
                    exercise_id=exercise.id if exercise else None,
                    exercise_slug=slug,
                    exercise_name=exercise.name if exercise else None,
                    via=item["via"],
                    note=slot.get("format")
                    or (f"только для цели: {slot['optional']}" if slot.get("optional") else None),
                )
            )
        days_out.append(DayOut(name=day["name"], slots=slots))
    volume = [
        VolumeOut(group=v["group"], name=UI_GROUPS.get(v["group"], v["group"]), sets=v["sets"])
        for v in programs.volume_by_group(db, volume_input)
    ]
    card = _card(row, profile, recommended)
    return ProgramDetail(
        **card.model_dump(),
        principle=spec["principle"],
        warning=spec.get("warning"),
        rules=spec.get("rules"),
        phases=spec.get("phases"),
        stages=spec.get("stages"),
        week_scheme=spec.get("week_scheme"),
        cardio=spec.get("cardio"),
        base_template=result["base_id"],
        days=days_out,
        volume=volume,
        empty_slots=result["resolved"]["empty"],
        inventory_used=profile["inventory"],
        level_used=profile["level"],
    )
