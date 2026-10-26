"""Матрица выбора шаблона: цель × дни × уровень × инвентарь (data/programs_T01-T22.md, 5.6).

Строки строятся из таблицы зала и переопределений по инвентарю и пишутся в БД (`template_matrix`),
поэтому выбор — это поиск строки, а не набор условий. Условия «перерыв», «50+», «сессия до 30 минут»
и «сплит по просьбе» — отдельные строки с полем `condition`.
"""

from typing import Any

from app.content.templates_data import TEMPLATES

GOALS = ("strength", "strength_mass", "mass", "return", "weight_loss", "general")
DAYS = (2, 3, 4, 5, 6)
LEVELS = ("beginner", "intermediate", "advanced")
CONDITION_ORDER = ("short30", "split", "age50", "break")
INVENTORY_PROFILES = ("gym", "home_barbell", "dumbbells", "bodyweight", "kettlebell")


def _all(*ids: str) -> dict[str, list[str]]:
    return {level: list(ids) for level in LEVELS}


def _lv(beginner: list[str], intermediate: list[str], advanced: list[str] | None = None) -> dict[str, list[str]]:
    return {"beginner": beginner, "intermediate": intermediate, "advanced": advanced or intermediate}


# Основная таблица (полный зал): цель → дни → уровень → шаблоны (первый — основной, остальные — следом).
GYM: dict[str, dict[int, dict[str, list[str]]]] = {
    "strength": {
        2: _all("T13", "T02"),
        3: _lv(["T02", "T03"], ["T04", "T06"], ["T21"]),
        4: _lv(["T03"], ["T05"], ["T05"]),
        5: _lv(["T03"], ["T22", "T10"], ["T22", "T10"]),
        6: _lv(["T03"], ["T10"], ["T10"]),
    },
    "strength_mass": {
        2: _all("T13"),
        3: _lv(["T02", "T03"], ["T09", "T04"], ["T09"]),
        4: _lv(["T03"], ["T07"], ["T07"]),
        5: _lv(["T03"], ["T10"], ["T10"]),
        6: _lv(["T11"], ["T11"], ["T10"]),
    },
    "mass": {
        2: _all("T13"),
        3: _lv(["T01", "T09"], ["T09"], ["T09"]),
        4: _lv(["T08"], ["T08"], ["T08"]),
        5: _lv(["T08"], ["T10"], ["T10"]),
        6: _lv(["T11"], ["T11"], ["T11"]),
    },
    "return": {d: _all("T14") for d in DAYS},
    "weight_loss": {
        2: _all("T13", "T18"),
        3: _all("T18"),
        4: _all("T18"),
        5: _all("T18"),
        6: _all("T18"),
    },
    "general": {d: _all("T19") for d in DAYS},
}

# Дом без стоек и штанги: что выбирается вместо зальной таблицы (по дням).
HOME_DEFAULT: dict[str, dict[int, list[str]]] = {
    "home_barbell": {2: ["T13"], 3: ["T09"], 4: ["T09"], 5: ["T09"], 6: ["T09"]},
    "dumbbells": {2: ["T13"], 3: ["T15"], 4: ["T15"], 5: ["T15"], 6: ["T15"]},
    "bodyweight": {2: ["T13"], 3: ["T16"], 4: ["T16"], 5: ["T16"], 6: ["T16"]},
    "kettlebell": {d: ["T17"] for d in DAYS},
}

NOTES = {
    "strength:beginner:5": "Новичку хватает четырёх тренировок; пятая и шестая добавят усталости, а не силы.",
    "strength:advanced:3": "Тяжёлые лесенки: прогрессия блоками пока ведётся как у T07.",
}


def _templates_by_id() -> dict[str, dict[str, Any]]:
    return {t["id"]: t for t in TEMPLATES}


def _for_inventory(goal: str, days: int, level: str, inventory: str) -> list[str]:
    ids = list(GYM[goal][days][level])
    if goal in ("return", "weight_loss"):
        return ids  # T14 и T18 сами подстраиваются под инвентарь
    if inventory == "gym":
        return ids
    by_id = _templates_by_id()
    if inventory == "kettlebell":
        return ["T17"] if goal != "general" else ["T17", "T19"]
    if goal == "general":
        return ids  # T19 рассчитан на любой инвентарь
    # «Только гантели» и «только вес тела» задаёт отдельное переопределение по дням
    if inventory in ("dumbbells", "bodyweight"):
        return list(HOME_DEFAULT[inventory][days])
    allowed = [t for t in ids if inventory in by_id[t]["inventory"]]
    return allowed or list(HOME_DEFAULT[inventory][days])


def build_matrix() -> list[dict[str, Any]]:
    """Все строки матрицы: основные (condition=None) и условные."""
    rows: list[dict[str, Any]] = []
    for goal in GOALS:
        for days in DAYS:
            for level in LEVELS:
                for inventory in INVENTORY_PROFILES:
                    rows.append(
                        {
                            "goal": goal,
                            "days": days,
                            "level": level,
                            "inventory": inventory,
                            "condition": None,
                            "mode": "base",
                            "templates": _for_inventory(goal, days, level, inventory),
                            "note": NOTES.get(f"{goal}:{level}:{days}"),
                        }
                    )
    # Условия применяются после основной матрицы (docs 5.6)
    rows += [
        {"goal": None, "days": None, "level": None, "inventory": None, "condition": "break",
         "mode": "prefix", "templates": ["T14"], "note": "Перерыв две недели и больше: сначала возвращение на 2–6 недель."},
        {"goal": None, "days": None, "level": None, "inventory": None, "condition": "age50",
         "mode": "prefix", "templates": ["T20"], "note": "От 50 лет основа: функциональная сила. Для 65+ с факторами риска нужен допуск врача."},
        {"goal": None, "days": None, "level": None, "inventory": None, "condition": "short30",
         "mode": "replace", "templates": ["T13"], "note": "Сессия не больше 30 минут: короткие суперсеты при любом числе дней."},
        {"goal": "mass", "days": None, "level": None, "inventory": "gym", "condition": "split",
         "mode": "prefix", "templates": ["T12"], "note": "Сплит по группам мышц: частота один раз в неделю ниже оптимальной."},
    ]
    return rows


def recommend(
    rows: list[dict[str, Any]],
    goal: str,
    days: int,
    level: str,
    inventory: str,
    conditions: set[str] | None = None,
) -> dict[str, Any]:
    """Шаблоны для ответов онбординга: основной, следующие за ним и пояснения."""
    conditions = conditions or set()
    base = next(
        r for r in rows
        if r["condition"] is None and r["goal"] == goal and r["days"] == days
        and r["level"] == level and r["inventory"] == inventory
    )
    result = list(base["templates"])
    reasons = [base["note"]] if base["note"] else []
    # Порядок важен: перерыв ставится последним, то есть оказывается первым в списке (T14 → T20 → …)
    ordered = sorted(
        (r for r in rows if r["condition"] in conditions),
        key=lambda r: CONDITION_ORDER.index(r["condition"]),
    )
    for row in ordered:
        if row["goal"] not in (None, goal) or row["inventory"] not in (None, inventory):
            continue
        reasons.append(row["note"])
        if row["mode"] == "replace":
            result = list(row["templates"])
        else:
            result = row["templates"] + [t for t in result if t not in row["templates"]]
    return {"primary": result[0], "then": result[1:], "reasons": [r for r in reasons if r], "base": base}
