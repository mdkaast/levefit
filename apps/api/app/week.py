"""Недельный план: направления → сессии → расстановка по дням без конфликтов, акценты, предпросмотр.

Принципы:
- Неделя замораживается при первом обращении (`WeekPlan`) и дальше не пересчитывается, поэтому смена
  направлений или акцента никогда не ломает идущую неделю.
- Акцент и новые направления действуют с ближайшего понедельника (`AccentVersion.effective_from`).
- Сессии бега, йоги, кроссфита и функционального тренинга пока заготовки, `verified=False`.
"""

from datetime import date, timedelta
from itertools import combinations, permutations
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import programs
from app.content import resolver
from app.content.directions import (
    ACCENT_ACCESSORY,
    ACCENT_EXTRA_SETS,
    ACCENT_MUSCLES,
    DEFAULT_QUALITY,
    DIRECTIONS,
    LEGACY_MUSCLES,
    MAX_DAYS_PER_DIRECTION,
    MAX_TRAINING_DAYS,
    POWERLIFTING_PATTERN,
    SESSION_TEMPLATES,
    WEEKLY_SETS_CAP,
    valid_accent,
)
from app.content.muscles import UI_GROUPS
from app.game import utcnow
from app.models import AccentVersion, User, UserDirection, WeekPlan

PLANNER_VERSION = "1.0"
HEAVY_PATTERNS = {"squat", "hinge", "lunge", "hip_extension"}
MAX_RUN = 3  # подряд идущих дней с занятиями не больше трёх
WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def next_monday(day: date) -> date:
    return monday_of(day) + timedelta(days=7)


# --- настройки пользователя -------------------------------------------------------------------


def saved_directions(db: Session, user: User) -> list[tuple[str, int]]:
    rows = db.scalars(
        select(UserDirection).where(UserDirection.user_id == user.id).order_by(UserDirection.sort)
    )
    return [(r.direction, r.days_per_week) for r in rows]


def effective_directions(db: Session, user: User) -> list[tuple[str, int]]:
    """Сохранённые направления; без них неделя строится из «Зала» или «Дома» по дням онбординга."""
    saved = saved_directions(db, user)
    if saved:
        return saved
    character = user.character
    days = character.workouts_per_week if character else 3
    home = character is not None and character.equipment != "gym"
    return [("home" if home else "gym", min(MAX_DAYS_PER_DIRECTION, max(1, days)))]


def accent_for(db: Session, user: User, direction: str, week_start: date) -> list[str]:
    """Акцент направления, действующий на неделю: последняя версия не позже её понедельника."""
    version = db.scalar(
        select(AccentVersion)
        .where(
            AccentVersion.user_id == user.id,
            AccentVersion.direction == direction,
            AccentVersion.effective_from <= week_start,
        )
        .order_by(AccentVersion.effective_from.desc(), AccentVersion.id.desc())
        .limit(1)
    )
    if version is not None:
        return list(version.selection)
    # Акцент, выбранный до фазы 3 в профиле (шесть групп), переносим в восемь новых.
    if direction == "gym" and user.character and user.character.target_muscles:
        mapped: list[str] = []
        for old in user.character.target_muscles:
            mapped.extend(m for m in LEGACY_MUSCLES.get(old, []) if m not in mapped)
        return mapped[:2]
    return []


def pending_accent(db: Session, user: User, today: date) -> dict[str, dict[str, Any]]:
    """Акценты, которые вступят в силу в следующий понедельник и отличаются от действующих."""
    start = next_monday(today)
    pending: dict[str, dict[str, Any]] = {}
    for direction, _ in effective_directions(db, user):
        now, later = (
            accent_for(db, user, direction, monday_of(today)),
            accent_for(db, user, direction, start),
        )
        if now != later:
            pending[direction] = {"from": start.isoformat(), "selection": later}
    return pending


# --- сборка сессий ---------------------------------------------------------------------------


def _inventory_for(direction: str, user: User, profile: dict[str, Any]) -> str:
    equipment = user.character.equipment if user.character else "gym"
    if direction == "home":
        return "bodyweight" if equipment == "none" else "dumbbells"
    if direction == "powerlifting":
        return "gym" if equipment == "gym" else "home_barbell"
    return profile["inventory"]


def _exercise_line(catalog: dict[str, dict[str, Any]], slot: dict[str, Any], slug: str) -> dict:
    return {
        "slug": slug,
        "exercise_id": catalog[slug]["id"],
        "name": catalog[slug]["name"],
        "sets": slot["sets"][0],
        "reps": list(slot["reps"]),
        "unit": "sec" if slot.get("progression") == "time" else "reps",
        "role": slot["role"],
        "pattern": slot["pattern"],
        "accent": None,
    }


def _strength_sessions(
    db: Session,
    user: User,
    direction: str,
    days: int,
    selection: list[str],
    catalog: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str], str | None]:
    profile = {**programs.profile_of(user)}
    inventory = _inventory_for(direction, user, profile)
    goal = "strength" if direction == "powerlifting" else profile["goal"]
    overrides = {"days": min(6, max(2, days)), "inventory": inventory, "goal": goal}
    rec = programs.recommend_for(db, user, overrides)
    if rec is None:
        return [], ["catalog_missing"], None
    usable, _ = programs.usable_template(db, rec["primary"])
    resolved = programs.resolve_for_user(db, usable, rec["profile"])["resolved"]["days"]
    if not resolved:
        return [], ["catalog_missing"], None

    sessions: list[dict[str, Any]] = []
    for index in range(days):
        day = resolved[index % len(resolved)]
        lines, heavy = [], False
        for item in day["slots"]:
            slot, slug = item["slot"], item["slug"]
            if slug is None or slug not in catalog or catalog[slug]["category"] != "strength":
                continue
            lines.append(_exercise_line(catalog, slot, slug))
            if slot["role"] == "main" and slot["pattern"] in HEAVY_PATTERNS:
                heavy = True
        sessions.append(
            {
                "key": f"{direction}:{index}",
                "title": f"{DIRECTIONS[direction]['name']} · {day['name']}",
                "direction": direction,
                "kind": "strength",
                "minutes": None,
                "hard": heavy,
                "tags": ["heavy_legs"] if heavy else [],
                "exercises": lines,
                "blocks": [],
                "verified": False,
            }
        )
    warnings: list[str] = []
    level = rec["profile"]["level"]
    if DIRECTIONS[direction]["accent"] == "muscles":
        warnings += _apply_muscle_accent(db, sessions, selection, catalog, inventory, level)
    elif direction == "powerlifting":
        _apply_lift_accent(sessions, selection)
    return sessions, warnings, usable


def _group_sets(db: Session, sessions: list[dict[str, Any]]) -> dict[str, float]:
    pairs = [(e["slug"], e["sets"]) for s in sessions for e in s["exercises"]]
    return {row["group"]: row["sets"] for row in programs.volume_by_group(db, pairs)}


def _apply_muscle_accent(
    db: Session,
    sessions: list[dict[str, Any]],
    selection: list[str],
    catalog: dict[str, dict[str, Any]],
    inventory: str,
    level: str,
) -> list[str]:
    """Каждой выбранной группе добавляем упражнение на 2 подхода в неделю, пока не выше потолка."""
    warnings: list[str] = []
    items = resolver.inventory_items(inventory)
    for key in selection:
        info, spec = ACCENT_MUSCLES.get(key), ACCENT_ACCESSORY.get(key)
        if info is None or spec is None or not sessions:
            continue
        groups = _group_sets(db, sessions)
        current = sum(groups.get(g, 0.0) for g in info["ui"])
        if current + ACCENT_EXTRA_SETS > WEEKLY_SETS_CAP:
            warnings.append(f"accent_capped:{key}")
            continue

        # день, где группа уже работает больше всего; без неё — самый короткий
        def load(session: dict[str, Any], ui: list[str] = info["ui"]) -> float:
            return sum(_group_sets(db, [session]).get(g, 0.0) for g in ui)

        target = max(sessions, key=lambda s: (load(s), -len(s["exercises"])))
        used = {e["slug"] for s in sessions for e in s["exercises"]}
        slot = {
            "pattern": spec["pattern"],
            "role": "accessory",
            "sets": [ACCENT_EXTRA_SETS, ACCENT_EXTRA_SETS],
            "reps": spec["reps"],
            "candidates": [c for c in spec["candidates"] if c not in used],
            "progression": "double",
        }
        found = resolver.resolve_slot(slot, catalog, items, level)
        if found.slug is None or found.slug in used:
            warnings.append(f"accent_unavailable:{key}")
            continue
        line = _exercise_line(catalog, slot, found.slug)
        line["accent"] = key
        target["exercises"].append(line)
    return warnings


def _apply_lift_accent(sessions: list[dict[str, Any]], selection: list[str]) -> None:
    """Пауэрлифтинг: акцент на присед, жим или тягу добавляет один подход на главное движение."""
    for key in selection:
        pattern = POWERLIFTING_PATTERN.get(key)
        if pattern is None:
            continue
        for session in sessions:
            lines = [
                e for e in session["exercises"] if e["pattern"] == pattern and e["role"] == "main"
            ]
            if lines:
                lines[0]["sets"] += 1
                lines[0]["accent"] = key
                break


def _other_sessions(direction: str, days: int, selection: list[str]) -> list[dict[str, Any]]:
    pool = SESSION_TEMPLATES.get(direction, [])
    wanted = selection or [DEFAULT_QUALITY.get(direction, "")]
    ordered = [t for t in pool if t["quality"] in wanted] + [
        t for t in pool if t["quality"] not in wanted
    ]
    hard_limit = max(1, days // 2)
    picked: list[dict[str, Any]] = []
    hard = 0
    for template in ordered:
        if len(picked) == days:
            break
        if template["hard"] and hard >= hard_limit:
            continue
        hard += template["hard"]
        picked.append(template)
    easy = [t for t in pool if not t["hard"]] or pool
    while len(picked) < days and easy:
        picked.append(easy[len(picked) % len(easy)])
    sessions = []
    for index, template in enumerate(picked):
        sessions.append(
            {
                "key": f"{direction}:{index}",
                "title": template["name"],
                "direction": direction,
                "kind": "session",
                "minutes": template["minutes"],
                "hard": template["hard"],
                "tags": list(template["tags"]),
                "exercises": [],
                "blocks": list(template["blocks"]),
                "verified": template["verified"],
                "quality": template["quality"],
            }
        )
    return sessions


# --- расстановка по дням ---------------------------------------------------------------------


def _conflict(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Соседние дни: тяжёлые ноги и интервалы друг рядом не ставим."""
    taxing = {"heavy_legs", "intervals"}
    return bool(taxing & set(a["tags"])) and bool(taxing & set(b["tags"]))


def violations(slots: list[dict[str, Any] | None]) -> list[dict[str, Any]]:
    """Нарушения правил в расписании из 7 дней (None — день отдыха)."""
    found: list[dict[str, Any]] = []
    run = 0
    for day, session in enumerate(slots):
        run = run + 1 if session else 0
        if run > MAX_RUN:
            found.append({"rule": "run", "day": day})
        nxt = slots[day + 1] if day + 1 < len(slots) else None
        if session and nxt and _conflict(session, nxt):
            found.append({"rule": "adjacent", "day": day})
    return found


def schedule(sessions: list[dict[str, Any]]) -> tuple[list[dict[str, Any] | None], list[dict]]:
    """Лучшая расстановка: меньше нарушений, затем ровнее промежутки, затем раньше по неделе.

    Порядок сессий одного направления сохраняется (A раньше B).
    """
    count = len(sessions)
    if count == 0:
        return [None] * 7, []
    best: tuple[Any, ...] | None = None
    chosen: list[dict[str, Any] | None] = [None] * 7
    for days in combinations(range(7), count):
        gaps = [b - a for a, b in zip(days, days[1:], strict=False)] + [days[0] + 7 - days[-1]]
        spread = sum((g - 7 / count) ** 2 for g in gaps)
        for order in permutations(range(count)):
            if not _keeps_direction_order(sessions, order):
                continue
            slots: list[dict[str, Any] | None] = [None] * 7
            for day, index in zip(days, order, strict=True):
                slots[day] = sessions[index]
            score = (len(violations(slots)), round(spread, 6), days, order)
            if best is None or score < best:
                best, chosen = score, slots
    return chosen, violations(chosen)


def _keeps_direction_order(sessions: list[dict[str, Any]], order: tuple[int, ...]) -> bool:
    seen: dict[str, int] = {}
    for index in order:
        direction = sessions[index]["direction"]
        number = int(sessions[index]["key"].split(":")[1])
        if number < seen.get(direction, -1):
            return False
        seen[direction] = number
    return True


# --- неделя целиком --------------------------------------------------------------------------


def build_week(
    db: Session,
    user: User,
    week_start: date,
    directions: list[tuple[str, int]],
    accents: dict[str, list[str]],
) -> dict[str, Any]:
    """Недельный план по заданным направлениям и акцентам (ничего не сохраняет)."""
    catalog = programs.load_catalog(db)
    sessions: list[dict[str, Any]] = []
    warnings: list[str] = []
    templates: dict[str, str] = {}
    resolved_directions = _expand_universal(directions)
    for direction, days in resolved_directions:
        info = DIRECTIONS.get(direction)
        if info is None or days <= 0:
            continue
        selection = accents.get(direction, [])
        if info["kind"] == "strength":
            built, notes, template = _strength_sessions(
                db, user, direction, days, selection, catalog
            )
            warnings += notes
            if template:
                templates[direction] = template
        else:
            built = _other_sessions(direction, days, selection)
        sessions.extend(built)

    dropped = len(sessions) - MAX_TRAINING_DAYS
    if dropped > 0:
        sessions = sessions[:MAX_TRAINING_DAYS]
        warnings.append(f"overload:{dropped}")
    slots, found = schedule(sessions)
    if found:
        warnings.append("conflicts")
    strength_pairs = [(e["slug"], e["sets"]) for s in sessions for e in s["exercises"]]
    return {
        "week_start": week_start.isoformat(),
        "planner_version": PLANNER_VERSION,
        "days": [
            {
                "date": (week_start + timedelta(days=i)).isoformat(),
                "weekday": i,
                "session": slots[i],
            }
            for i in range(7)
        ],
        "volume": [
            {**row, "name": UI_GROUPS.get(row["group"], row["group"])}
            for row in programs.volume_by_group(db, strength_pairs)
        ],
        "warnings": warnings,
        "violations": found,
        "templates": templates,
        "accents": {d: accents.get(d, []) for d, _ in resolved_directions},
    }


def _expand_universal(directions: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """«Универсальный» без других направлений работает как зал; с другими не добавляет занятий."""
    others = [(d, n) for d, n in directions if d != "universal"]
    if others:
        return others
    days = max((n for d, n in directions if d == "universal"), default=0)
    return [("gym", days)] if days else []


def ensure_week(db: Session, user: User, week_start: date) -> dict[str, Any]:
    """Замороженный план недели; при первом обращении строится по настройкам на её понедельник."""
    existing = db.scalar(
        select(WeekPlan).where(WeekPlan.user_id == user.id, WeekPlan.week_start == week_start)
    )
    if existing is not None:
        return existing.spec
    directions = effective_directions(db, user)
    accents = {d: accent_for(db, user, d, week_start) for d, _ in directions}
    spec = build_week(db, user, week_start, directions, accents)
    # Пока направления не сохранены, пользователь не «на программе»: показываем план «на лету»,
    # чтобы первое сохранение направлений не упиралось в замороженную по умолчанию неделю.
    if saved_directions(db, user):
        db.add(WeekPlan(user_id=user.id, week_start=week_start, spec=spec))
        db.flush()
    return spec


def upcoming_week(db: Session, user: User, today: date) -> dict[str, Any]:
    """Как будет выглядеть следующая неделя при текущих настройках (не сохраняется)."""
    start = next_monday(today)
    existing = db.scalar(
        select(WeekPlan).where(WeekPlan.user_id == user.id, WeekPlan.week_start == start)
    )
    if existing is not None:
        return existing.spec
    directions = effective_directions(db, user)
    accents = {d: accent_for(db, user, d, start) for d, _ in directions}
    return build_week(db, user, start, directions, accents)


def session_for(db: Session, user: User, day: date) -> dict[str, Any] | None:
    spec = ensure_week(db, user, monday_of(day))
    return spec["days"][day.weekday()]["session"]


def follows_week(db: Session, user: User) -> bool:
    """План «Сегодня» идёт по неделе только у сохранивших направления («перейти на программу»)."""
    return bool(saved_directions(db, user))


# --- изменения настроек ----------------------------------------------------------------------


class InvalidChange(ValueError):
    pass


def validate_directions(items: list[tuple[str, int]]) -> list[tuple[str, int]]:
    seen: set[str] = set()
    for direction, days in items:
        if direction not in DIRECTIONS:
            raise InvalidChange(f"direction:{direction}")
        if direction in seen:
            raise InvalidChange(f"duplicate:{direction}")
        if not 0 <= days <= MAX_DAYS_PER_DIRECTION:
            raise InvalidChange(f"days:{direction}")
        seen.add(direction)
    kept = [(d, n) for d, n in items if n > 0 or d == "universal"]
    if not kept:
        raise InvalidChange("empty")
    return kept


def set_directions(db: Session, user: User, items: list[tuple[str, int]], today: date) -> None:
    """Сохраняет направления; идущая неделя сначала замораживается и не меняется."""
    kept = validate_directions(items)
    if saved_directions(db, user):
        ensure_week(db, user, monday_of(today))  # идущая неделя остаётся прежней
    else:
        # Первый переход на программу: прежней недели не было, новая начинается сразу.
        for old in db.scalars(select(WeekPlan).where(WeekPlan.user_id == user.id)):
            db.delete(old)
    for row in db.scalars(select(UserDirection).where(UserDirection.user_id == user.id)):
        db.delete(row)
    db.flush()
    for index, (direction, days) in enumerate(kept):
        db.add(UserDirection(user_id=user.id, direction=direction, days_per_week=days, sort=index))
    db.flush()


def set_accent(db: Session, user: User, direction: str, selection: list[str], today: date) -> date:
    """Новый акцент вступает в силу в ближайший понедельник; текущая неделя остаётся прежней."""
    if direction not in DIRECTIONS or not valid_accent(direction, selection):
        raise InvalidChange(f"accent:{direction}")
    ensure_week(db, user, monday_of(today))
    start = next_monday(today)
    db.query(AccentVersion).filter(
        AccentVersion.user_id == user.id,
        AccentVersion.direction == direction,
        AccentVersion.effective_from == start,
    ).delete()
    db.add(
        AccentVersion(
            user_id=user.id, direction=direction, selection=selection, effective_from=start
        )
    )
    db.flush()
    return start


# --- предпросмотр «до / после» ---------------------------------------------------------------


def _lines(session: dict[str, Any] | None) -> dict[str, tuple[int, str]]:
    if not session:
        return {}
    if session["kind"] == "session":
        return {session["title"]: (0, session["title"])}
    return {e["slug"]: (e["sets"], e["name"]) for e in session["exercises"]}


def diff_weeks(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    """Что изменится по дням: сессии добавились, исчезли или поменялись упражнения и подходы."""
    changes: list[dict[str, Any]] = []
    for old, new in zip(before["days"], after["days"], strict=True):
        a, b = old["session"], new["session"]
        if a is None and b is None:
            continue
        day = WEEKDAYS[old["weekday"]]
        if a is None:
            changes.append(
                {
                    "weekday": old["weekday"],
                    "day": day,
                    "kind": "added",
                    "title": b["title"],
                    "details": [],
                }
            )
        elif b is None:
            changes.append(
                {
                    "weekday": old["weekday"],
                    "day": day,
                    "kind": "removed",
                    "title": a["title"],
                    "details": [],
                }
            )
        else:
            before_lines, after_lines = _lines(a), _lines(b)
            details = []
            for slug, (sets, name) in after_lines.items():
                if slug not in before_lines:
                    details.append(f"+ {name}: {sets} подх." if sets else f"+ {name}")
                elif before_lines[slug][0] != sets:
                    details.append(f"{name}: {before_lines[slug][0]} → {sets} подх.")
            details += [
                f"− {name}" for slug, (_, name) in before_lines.items() if slug not in after_lines
            ]
            if details or a["title"] != b["title"]:
                changes.append(
                    {
                        "weekday": old["weekday"],
                        "day": day,
                        "kind": "changed",
                        "title": b["title"],
                        "details": details,
                    }
                )
    return changes


def volume_delta(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    old = {v["group"]: v["sets"] for v in before["volume"]}
    new = {v["group"]: v["sets"] for v in after["volume"]}
    rows = [
        {
            "group": g,
            "name": UI_GROUPS.get(g, g),
            "before": old.get(g, 0.0),
            "after": new.get(g, 0.0),
        }
        for g in sorted(set(old) | set(new))
        if round(old.get(g, 0.0) - new.get(g, 0.0), 1) != 0
    ]
    return sorted(rows, key=lambda r: -abs(r["after"] - r["before"]))


def preview(
    db: Session,
    user: User,
    today: date,
    directions: list[tuple[str, int]] | None = None,
    accent: tuple[str, list[str]] | None = None,
) -> dict[str, Any]:
    """«До / после» для следующей недели при смене направлений и/или акцента."""
    start = next_monday(today)
    current_directions = effective_directions(db, user)
    before = upcoming_week(db, user, today)
    new_directions = (
        validate_directions(directions) if directions is not None else current_directions
    )
    accents = {d: accent_for(db, user, d, start) for d, _ in new_directions}
    if accent is not None:
        direction, selection = accent
        if direction not in DIRECTIONS or not valid_accent(direction, selection):
            raise InvalidChange(f"accent:{direction}")
        accents[direction] = selection
    after = build_week(db, user, start, new_directions, accents)
    return {
        "effective_from": start.isoformat(),
        "current_week_unchanged": True,
        "changes": diff_weeks(before, after),
        "volume": volume_delta(before, after),
        "before": before,
        "after": after,
    }


def today() -> date:
    return utcnow().date()


# --- план «Сегодня» по неделе -----------------------------------------------------------------


def planned_session(
    db: Session, user: User, day: date
) -> tuple[dict[str, Any] | None, date | None]:
    """Сессия на день; в день отдыха — ближайшая впереди по неделе, чтобы можно было начать."""
    spec = ensure_week(db, user, monday_of(day))
    days = spec["days"]
    own = days[day.weekday()]["session"]
    if own is not None:
        return own, day
    for item in days[day.weekday() + 1 :] + days[: day.weekday()]:
        if item["session"] is not None:
            return item["session"], date.fromisoformat(item["date"])
    return None, None


def _known_weights(db: Session, user: User, exercise_ids: list[int]) -> dict[int, float]:
    """Рабочий вес: цель из последнего решения движка, иначе лучший вес прошлой тренировки."""
    from app.ai.schema import Adjustment
    from app.models import AiAdjustment, Workout, WorkoutSet

    found: dict[int, float] = {}
    rows = db.scalars(
        select(AiAdjustment)
        .join(Workout, Workout.id == AiAdjustment.workout_id)
        .where(Workout.user_id == user.id)
        .order_by(AiAdjustment.id.desc())
        .limit(10)
    )
    for row in rows:
        for item in Adjustment.model_validate(row.result).next_workout:
            if item.target_weight_kg is not None and item.exercise_id not in found:
                found[item.exercise_id] = item.target_weight_kg
    for exercise_id in exercise_ids:
        if exercise_id in found:
            continue
        last = db.scalar(
            select(WorkoutSet.workout_id)
            .join(Workout, Workout.id == WorkoutSet.workout_id)
            .where(Workout.user_id == user.id, WorkoutSet.exercise_id == exercise_id)
            .order_by(Workout.date.desc(), Workout.id.desc())
            .limit(1)
        )
        if last is None:
            continue
        weights = [
            s.weight_kg
            for s in db.scalars(
                select(WorkoutSet).where(
                    WorkoutSet.workout_id == last, WorkoutSet.exercise_id == exercise_id
                )
            )
            if s.weight_kg
        ]
        if weights:
            found[exercise_id] = max(weights)
    return found


def plan_items(db: Session, user: User, session: dict[str, Any]) -> list[dict[str, Any]]:
    """Упражнения сессии как план тренировки: подходы и повторы из недели, вес из движка."""
    lines = [e for e in session["exercises"] if e["unit"] == "reps"]
    weights = _known_weights(db, user, [e["exercise_id"] for e in lines])
    return [
        {
            "exercise_id": e["exercise_id"],
            "name": e["name"],
            "target_weight_kg": weights.get(e["exercise_id"]),
            "sets": e["sets"],
            "reps": e["reps"][1],
        }
        for e in lines
    ]
