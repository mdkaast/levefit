"""Цель по калориям и БЖУ: формула с видимыми допущениями и защитные правила (F3, F4).

Чистые функции без БД. Все числа здесь допущения продукта, а не медицинские рекомендации:
правила защиты (нижняя граница, предел дефицита) ждут утверждения врачом или диетологом (F4),
пока это записано в `docs/nutrition.md`.

Источники: формула Миффлина и Сан-Жеора для базового обмена; коэффициенты активности из общепринятой
таблицы; белок 1,8 г/кг и жиры 1 г/кг по ТЗ; темп снижения 0,5% массы в неделю и ограничение до 1%
по data/programming_rules.md (4.8); не предлагать дефицит при признаках РПП, очень низком ИМТ,
аменорее, обмороках, беременности и кормлении по data/safety_screening.md.
"""

from dataclasses import dataclass, field

MODES = ("gain", "maintain", "lose")
ACTIVITY = {"sedentary": 1.2, "light": 1.375, "active": 1.55, "very_active": 1.725}
DEFAULT_ACTIVITY = 1.375
ACTIVITY_NAMES = {
    "sedentary": "малоподвижный образ жизни",
    "light": "лёгкая активность",
    "active": "активный образ жизни",
    "very_active": "очень активный образ жизни",
}

GAIN_SURPLUS = 0.10  # прибавка к расходу при наборе массы
LOSE_WEEKLY_RATE = 0.005  # 0,5% массы тела в неделю
KCAL_PER_KG = 7700
MAX_DEFICIT_SHARE = 0.20  # умеренный дефицит: не больше 20% расхода
ADJUST_STEP, ADJUST_MAX = 50, 300
PROTEIN_G_PER_KG, FAT_G_PER_KG = 1.8, 1.0
PROTEIN_MIN_G_PER_KG, FAT_MIN_G_PER_KG = 1.6, 0.8
KCAL_FLOOR = {
    "male": 1500,
    "female": 1200,
    "other": 1200,
}  # нижняя граница, не ниже базового обмена
MIN_BMI = 18.5
MIN_ADULT_AGE = 18

# Признаки, при которых дефицит не предлагается (data/safety_screening.md)
SCREENING = {
    "eating_disorder": "расстройство пищевого поведения в прошлом или сейчас",
    "pregnant_or_nursing": "беременность или кормление грудью",
    "fainting_or_amenorrhea": "обмороки или отсутствие менструаций",
}
AUTO_BLOCKS = {"low_bmi": "индекс массы тела ниже 18,5", "minor": "возраст младше 18 лет"}


@dataclass
class Profile:
    sex: str  # male | female | other
    age: int | None
    height_cm: int | None
    weight_kg: float | None
    lifestyle: str | None = None


@dataclass
class Goal:
    mode: str
    kcal: int
    protein_g: int
    fat_g: int
    carbs_g: int
    bmr: int
    tdee: int
    floor: int
    delta_kcal: int
    adjust_kcal: int
    assumptions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    clamped: bool = False


def _n(value: float) -> str:
    """Число с десятичной запятой: 1,375."""
    return f"{value:g}".replace(".", ",")


def bmr(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    """Миффлин и Сан-Жеор; для «не указан» берётся среднее мужской и женской констант."""
    constant = {"male": 5, "female": -161}.get(sex, -78)
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + constant


def bmi(weight_kg: float | None, height_cm: float | None) -> float | None:
    if not weight_kg or not height_cm:
        return None
    return weight_kg / (height_cm / 100) ** 2


def blocks_for(profile: Profile, flags: list[str]) -> list[str]:
    """Причины, по которым дефицит недоступен: отмеченное пользователем и вычисленное по профилю."""
    found = [f for f in flags if f in SCREENING]
    value = bmi(profile.weight_kg, profile.height_cm)
    if value is not None and value < MIN_BMI:
        found.append("low_bmi")
    if profile.age is not None and profile.age < MIN_ADULT_AGE:
        found.append("minor")
    return found


def round_to(value: float, step: int = 5) -> int:
    return int(round(value / step) * step)


def clamp_adjust(value: int) -> int:
    value = max(-ADJUST_MAX, min(ADJUST_MAX, value))
    return int(round(value / ADJUST_STEP) * ADJUST_STEP)


def compute(profile: Profile, mode: str, adjust_kcal: int, flags: list[str]) -> Goal | None:
    """Суточная цель; None, если для расчёта не хватает веса, роста или возраста."""
    if not (profile.weight_kg and profile.height_cm and profile.age):
        return None
    weight = profile.weight_kg
    base = bmr(profile.sex, weight, profile.height_cm, profile.age)
    factor = ACTIVITY.get(profile.lifestyle or "", DEFAULT_ACTIVITY)
    tdee = base * factor
    floor = max(KCAL_FLOOR.get(profile.sex, 1200), round_to(base))
    notes: list[str] = []
    assumptions = [
        f"Базовый обмен {round_to(base)} ккал: формула Миффлина и Сан-Жеора (возраст, рост, вес).",
        f"Расход {round_to(tdee)} ккал: базовый обмен × {_n(factor)} "
        f"({ACTIVITY_NAMES.get(profile.lifestyle or '', 'лёгкая активность по умолчанию')}).",
    ]
    if profile.sex == "other":
        assumptions.append("Пол не указан: взято среднее значение формулы.")

    blocked = blocks_for(profile, flags)
    effective = mode
    if mode == "lose" and blocked:
        effective = "maintain"
        notes.append("Дефицит калорий не предлагается. Обсудите питание с врачом или диетологом.")

    delta = 0
    if effective == "gain":
        delta = round_to(tdee * GAIN_SURPLUS)
        assumptions.append(f"Набор массы: плюс {GAIN_SURPLUS:.0%} к расходу, около {delta} ккал.")
    elif effective == "lose":
        wanted = weight * LOSE_WEEKLY_RATE * KCAL_PER_KG / 7
        capped = min(wanted, tdee * MAX_DEFICIT_SHARE)
        delta = -round_to(capped)
        assumptions.append(
            f"Снижение веса: около {LOSE_WEEKLY_RATE:.1%} массы тела в неделю, дефицит "
            f"{-delta} ккал и не больше {MAX_DEFICIT_SHARE:.0%} расхода."
        )
    else:
        assumptions.append("Поддержание: калории равны расходу.")

    adjust = clamp_adjust(adjust_kcal)
    if adjust:
        assumptions.append(f"Ручная поправка {adjust:+d} ккал.")
    kcal = tdee + delta + adjust
    clamped = False
    if effective == "lose" and kcal < floor:
        kcal, clamped = floor, True
        notes.append(f"Нижняя граница {floor} ккал: ниже в приложении цель не ставится.")
    elif kcal < floor:
        kcal, clamped = floor, True
        notes.append(f"Нижняя граница {floor} ккал: ниже цель не опускается.")
    kcal_i = round_to(kcal)

    protein = PROTEIN_G_PER_KG * weight
    fat = FAT_G_PER_KG * weight
    carbs = (kcal_i - protein * 4 - fat * 9) / 4
    if carbs < 0:
        protein = PROTEIN_MIN_G_PER_KG * weight
        carbs = (kcal_i - protein * 4 - fat * 9) / 4
    if carbs < 0:
        fat = FAT_MIN_G_PER_KG * weight
        carbs = (kcal_i - protein * 4 - fat * 9) / 4
    carbs = max(0.0, carbs)
    assumptions.append(
        f"Белок {_n(PROTEIN_G_PER_KG)} г на кг, жиры {_n(FAT_G_PER_KG)} г на кг, углеводы остаток."
    )
    return Goal(
        mode=effective,
        kcal=kcal_i,
        protein_g=round(protein),
        fat_g=round(fat),
        carbs_g=round(carbs),
        bmr=round_to(base),
        tdee=round_to(tdee),
        floor=floor,
        delta_kcal=delta,
        adjust_kcal=adjust,
        assumptions=assumptions,
        notes=notes,
        clamped=clamped,
    )


def weight_trend_hint(recent: list[float], previous: list[float]) -> str | None:
    """Подсказка, если вес падает быстрее 1% массы в неделю (две недели средних значений)."""
    if len(recent) < 2 or len(previous) < 2:
        return None
    last, before = sum(recent) / len(recent), sum(previous) / len(previous)
    if before <= 0:
        return None
    if (before - last) / before * 100 > 1.0:
        return (
            "Вес снижается быстрее ориентира 0,5–1% массы в неделю. "
            "Можно добавить 100–200 ккал; при плохом самочувствии обратитесь к врачу."
        )
    return None
