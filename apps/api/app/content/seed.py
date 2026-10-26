"""Импорт каталога упражнений, шаблонов программ и матрицы в БД.

Запуск: `python -m app.content.seed` (образ API выполняет его при старте после миграций).
Импорт идемпотентен и ничего не удаляет: упражнения находятся по `slug`; 24 упражнения из
прежнего справочника сопоставляются по названию и сохраняют свои `id`, поэтому история
подходов не теряется. Пользовательские упражнения не затрагиваются.
"""

import json
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.content.matrix import build_matrix
from app.content.muscles import MUSCLES
from app.content.templates_data import TEMPLATES
from app.models import Exercise, ExerciseMuscle, Muscle, ProgramTemplate, TemplateMatrix

CONTENT = Path(__file__).parent

# Прежнее название в справочнике → slug каталога. Остальные прежние упражнения остаются как есть.
LEGACY_NAMES = {
    "Приседания со штангой": "back_squat_high_bar",
    "Румынская тяга": "romanian_deadlift_bb",
    "Выпады": "forward_lunge",
    "Жим ног": "leg_press_45",
    "Жим лёжа": "barbell_bench_press",
    "Жим гантелей на наклонной": "incline_dumbbell_press",
    "Отжимания": "push_up",
    "Становая тяга": "deadlift_conventional",
    "Тяга штанги в наклоне": "barbell_bent_over_row",
    "Подтягивания": "pull_up",
    "Тяга верхнего блока": "lat_pulldown_wide",
    "Жим стоя": "barbell_overhead_press",
    "Махи гантелей в стороны": "dumbbell_lateral_raise",
    "Подъём штанги на бицепс": "barbell_curl",
    "Французский жим": "skull_crusher_ez",
    "Планка": "plank",
    "Скручивания": "crunch",
    "Велотренажёр": "cond_bike",
    "Гребной тренажёр": "cond_rower",
    "Скакалка": "cond_jump_rope",
    "Растяжка задней поверхности бедра": "mob_hamstring",
    "Кошка-корова": "wu_cat_cow",
}


def load_catalog() -> list[dict]:
    return json.loads((CONTENT / "exercises.json").read_text(encoding="utf-8"))


def seed_catalog(db: Session) -> dict[str, int]:
    """Загружает каталог, шаблоны и матрицу. Возвращает счётчики для отчёта."""
    stats = {"created": 0, "matched_legacy": 0, "updated": 0, "templates": 0, "matrix": 0}

    muscles = {m.slug: m for m in db.scalars(select(Muscle))}
    for slug, (name, group) in MUSCLES.items():
        row = muscles.get(slug)
        if row is None:
            row = Muscle(slug=slug, name_ru=name, ui_group=group)
            db.add(row)
            muscles[slug] = row
        else:
            row.name_ru, row.ui_group = name, group
    db.flush()

    by_slug = {e.slug: e for e in db.scalars(select(Exercise).where(Exercise.slug.is_not(None)))}
    legacy = {
        e.name: e
        for e in db.scalars(
            select(Exercise).where(Exercise.slug.is_(None), Exercise.owner_id.is_(None))
        )
    }
    slug_to_legacy_name = {slug: name for name, slug in LEGACY_NAMES.items()}

    touched: list[tuple[Exercise, list[dict]]] = []
    for item in load_catalog():
        slug = item["slug"]
        row = by_slug.get(slug)
        if row is None:
            old = legacy.get(slug_to_legacy_name.get(slug, ""))
            if old is not None:
                row = old
                stats["matched_legacy"] += 1
            else:
                row = Exercise(owner_id=None)
                db.add(row)
                stats["created"] += 1
        else:
            stats["updated"] += 1
        row.slug = slug
        row.name = item["name_ru"][:120]
        row.name_en = item["name_en"]
        row.category = item["category"]
        row.muscle_group = item["legacy_group"]
        row.pattern = item["pattern"]
        row.pattern_secondary = item["pattern_secondary"]
        row.level = item["level"]
        row.unilateral = item["unilateral"]
        row.equipment = item["equipment"]
        row.load_type = item["load_type"]
        row.load_increment_kg = item["load_increment_kg"]
        row.load_increment_beginner_kg = item["load_increment_beginner_kg"]
        row.e1rm = item["e1rm"]
        row.caution_flags = item["caution_flags"]
        row.subs = item["subs"]
        row.aliases = item["aliases"]
        row.variant_of = item["variant_of"]
        row.ui_groups = item["ui_groups"]
        row.is_active = True
        row.verified = item["verified"]
        row.source = "catalog"
        by_slug[slug] = row
        touched.append((row, item["muscles"]))
    db.flush()

    # Мышцы упражнений пересоздаём целиком: так повторный импорт даёт тот же результат.
    db.execute(delete(ExerciseMuscle).where(ExerciseMuscle.exercise_id.in_([r.id for r, _ in touched])))
    for row, links in touched:
        for link in links:
            muscle = muscles.get(link["muscle"])
            if muscle is not None:
                db.add(
                    ExerciseMuscle(
                        exercise_id=row.id,
                        muscle_id=muscle.id,
                        role=link["role"],
                        volume_weight=link["volume_weight"],
                    )
                )

    existing = {t.id: t for t in db.scalars(select(ProgramTemplate))}
    for spec in TEMPLATES:
        row = existing.get(spec["id"]) or ProgramTemplate(id=spec["id"])
        row.name, row.summary = spec["name"], spec["summary"]
        row.goals, row.levels = spec["goals"], spec["levels"]
        row.days_min, row.days_max = min(spec["days"]), max(spec["days"])
        row.inventory = spec["inventory"]
        row.progression = spec["progression"]
        row.engine_ready = spec["engine_ready"]
        row.fallback = spec.get("fallback")
        row.verified = False
        row.spec = spec
        db.add(row)
        stats["templates"] += 1

    db.execute(delete(TemplateMatrix))
    for r in build_matrix():
        db.add(TemplateMatrix(**r))
        stats["matrix"] += 1
    db.commit()
    return stats


def main() -> None:
    from app.db import SessionLocal

    with SessionLocal() as db:
        print("catalog seed:", seed_catalog(db))
        from app.content.seed_nutrition import seed_nutrition

        print("nutrition seed:", seed_nutrition(db))


if __name__ == "__main__":
    main()
