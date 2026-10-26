"""Подбор упражнения в слот шаблона: инвентарь, уровень, флаги нагрузки. Чистые функции без БД."""

from dataclasses import dataclass
from typing import Any

LEVELS = ("beginner", "intermediate", "advanced")

ALL_GYM = {
    "barbell", "ez_bar", "dumbbell", "kettlebell", "cable", "machine_stack", "plate_machine", "smith",
    "rack", "bench", "landmine", "trap_bar", "pullup_bar", "dip_bars", "rings", "band", "assist_machine",
    "bodyweight", "ghd", "plates", "jump_rope", "sled", "cardio_machine", "special_bar",
}

# Профили инвентаря из онбординга (docs: матрица выбора, переопределения по инвентарю)
INVENTORIES: dict[str, set[str]] = {
    "gym": ALL_GYM,
    "home_barbell": {"barbell", "rack", "bench", "plates", "pullup_bar", "band", "bodyweight", "jump_rope"},
    "dumbbells": {"dumbbell", "bodyweight"},
    "bodyweight": {"bodyweight"},
    "kettlebell": {"kettlebell", "bodyweight"},
}

# Жалоба на зону → флаги нагрузки, которые такие упражнения исключают (data/safety_screening.md, 6.3)
ZONE_FLAGS: dict[str, set[str]] = {
    "knee": {"deep_knee_flexion", "knee_pain", "patellofemoral_sensitive", "high_impact"},
    "low_back": {"axial_spinal_load", "lumbar_flexion_load", "lumbar_extension_load", "hernia_valsalva"},
    "shoulder": {"shoulder_2", "shoulder_3", "shoulder_end_range", "impingement_position"},
    "elbow_wrist": {"elbow_2", "elbow_3", "wrist_2", "wrist_3"},
    "neck": {"neck_strain", "inverted"},
    "hip": {"hip_impingement_deep_flexion", "hernia_valsalva"},
}

# Если в паттерне нет подходящего упражнения (например, нет турника), берём соседний паттерн.
PATTERN_FALLBACKS: dict[str, list[str]] = {
    "vertical_pull": ["horizontal_pull"],
    "vertical_push": ["horizontal_push"],
    "horizontal_pull": ["vertical_pull"],
    "knee_extension": ["squat", "lunge"],
    "knee_flexion": ["hinge", "hip_extension"],
    "hinge": ["hip_extension", "knee_flexion"],
    "hip_extension": ["hinge"],
    "calf_raise": ["lunge"],
    "chest_isolation": ["horizontal_push"],
    "shoulder_isolation": ["vertical_push", "rear_delt"],
    "rear_delt": ["horizontal_pull"],
    "elbow_flexion": ["vertical_pull", "horizontal_pull"],
    "elbow_extension": ["horizontal_push"],
    "scapular": ["horizontal_pull"],
    "core_anti_rotation": ["core_anti_extension"],
    "core_flexion": ["core_anti_extension"],
    "core_rotation": ["core_anti_rotation", "core_anti_extension"],
    "core_extension": ["core_anti_extension"],
    "carry": ["core_anti_rotation", "core_anti_extension"],
    "kb_skill": ["hinge"],
}


def inventory_items(profile: str, extras: set[str] | None = None) -> set[str]:
    return set(INVENTORIES[profile]) | (extras or set())


def available(exercise: dict[str, Any], inventory: set[str]) -> bool:
    """Подходит, если выполнена хотя бы одна альтернатива инвентаря целиком."""
    return any(all(item in inventory for item in alt) for alt in exercise["equipment"])


def blocked_flags(zones: set[str]) -> set[str]:
    flags: set[str] = set()
    for zone in zones:
        flags |= ZONE_FLAGS.get(zone, set())
    return flags


def excluded(exercise: dict[str, Any], flags: set[str]) -> bool:
    return bool(flags & set(exercise.get("caution_flags", [])))


def level_ok(exercise: dict[str, Any], level: str) -> bool:
    return LEVELS.index(exercise["level"]) <= LEVELS.index(level)


@dataclass
class Resolved:
    slug: str | None
    via: str  # candidate | pattern | neighbour_pattern | none


def resolve_slot(
    slot: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    inventory: set[str],
    level: str,
    flags: set[str] | None = None,
) -> Resolved:
    flags = flags or set()
    # 1. кандидаты шаблона в заданном порядке; им доверяем независимо от уровня упражнения
    for slug in slot["candidates"]:
        ex = catalog.get(slug)
        if ex and available(ex, inventory) and not excluded(ex, flags):
            return Resolved(slug, "candidate")

    def from_pattern(pattern: str, via: str) -> Resolved | None:
        pool = [
            e
            for e in catalog.values()
            if e["pattern"] == pattern
            and e["category"] == "strength"
            and available(e, inventory)
            and not excluded(e, flags)
            and level_ok(e, level)
        ]
        if not pool:
            return None
        # ближе к исходным кандидатам по группам мышц и проще по уровню
        wanted: set[str] = set()
        for slug in slot["candidates"]:
            if slug in catalog:
                wanted |= set(catalog[slug]["ui_groups"])
        pool.sort(key=lambda e: (-len(wanted & set(e["ui_groups"])), LEVELS.index(e["level"]), e["slug"]))
        return Resolved(pool[0]["slug"], via)

    # 2. тот же паттерн, 3. соседний паттерн
    found = from_pattern(slot["pattern"], "pattern")
    if found:
        return found
    for neighbour in PATTERN_FALLBACKS.get(slot["pattern"], []):
        found = from_pattern(neighbour, "neighbour_pattern")
        if found:
            return found
    return Resolved(None, "none")


def resolve_template(
    template: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    inventory: set[str],
    level: str,
    flags: set[str] | None = None,
) -> dict[str, Any]:
    """Дни шаблона с конкретными упражнениями; `empty` — слоты, для которых ничего не нашлось."""
    days = []
    empty: list[str] = []
    for day in template["days_spec"]:
        slots = []
        for slot in day["slots"]:
            result = resolve_slot(slot, catalog, inventory, level, flags)
            if result.slug is None:
                empty.append(f"{template['id']}/{day['name']}/{slot['pattern']}")
            slots.append({"slot": slot, "slug": result.slug, "via": result.via})
        days.append({"name": day["name"], "slots": slots})
    return {"id": template["id"], "days": days, "empty": empty}
