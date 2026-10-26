"""Шаблоны программ T01–T22 как данные (источник: data/programs_T01-T22.md, раздел 5).

Шаблон — список дней, день — список слотов: паттерн движения, роль, подходы × повторения, модель
прогрессии и упорядоченный список упражнений-кандидатов. Конкретное упражнение подбирается по
инвентарю, уровню и флагам нагрузки (app/content/resolver.py). Названия нейтральные: оригинальные
бренды программ не используются, принцип указан в `principle`.

Что данные не обещают:
- `engine_ready=False` — модель прогрессии (линейная за сессию, стадии, волны с процентами) движок
  пока не выполняет; пока рекомендуется `fallback` с двойной прогрессией;
- все шаблоны `verified=False`: ревью тренером и врачом ЛФК (D8) не проведено.
"""

from typing import Any

SQ, HG, LU, HE = "squat", "hinge", "lunge", "hip_extension"
KE, KF, CA = "knee_extension", "knee_flexion", "calf_raise"
HPU, VPU, CHI, SHI, EE = "horizontal_push", "vertical_push", "chest_isolation", "shoulder_isolation", "elbow_extension"
VPL, HPL, SC, RD, EF = "vertical_pull", "horizontal_pull", "scapular", "rear_delt", "elbow_flexion"
CAE, CAR, CFL, CRO, CEX = "core_anti_extension", "core_anti_rotation", "core_flexion", "core_rotation", "core_extension"
CR, KB, COND, MOB, WU = "carry", "kb_skill", "conditioning", "mobility", "warmup"


def S(pattern, role, sets, reps, cands, rir=None, prog="double", **extra) -> dict[str, Any]:
    """Слот: sets — число или (мин, макс), reps — (мин, макс), cands — упражнения по убыванию предпочтения."""
    slot: dict[str, Any] = {
        "pattern": pattern,
        "role": role,
        "sets": list(sets) if isinstance(sets, tuple) else [sets, sets],
        "reps": list(reps),
        "candidates": list(cands),
        "progression": prog,
    }
    if rir is not None:
        slot["rir"] = list(rir) if isinstance(rir, tuple) else [rir, rir]
    slot.update(extra)
    return slot


def D(name, *slots) -> dict[str, Any]:
    return {"name": name, "slots": list(slots)}


# Типовые наборы кандидатов (зал → дом → запасные)
SQUAT_MAIN = ["back_squat_high_bar", "front_squat", "goblet_squat", "bodyweight_squat"]
BENCH_MAIN = ["barbell_bench_press", "dumbbell_bench_press", "machine_chest_press", "push_up"]
ROW_MAIN = ["barbell_bent_over_row", "one_arm_dumbbell_row", "seated_cable_row", "door_towel_row"]
PULL_V = ["lat_pulldown_wide", "pull_up", "chin_up", "band_lat_pulldown", "negative_pull_up"]
OHP = ["barbell_overhead_press", "dumbbell_shoulder_press_seated", "dumbbell_shoulder_press_standing", "pike_push_up"]
HINGE_MAIN = ["deadlift_conventional", "romanian_deadlift_bb", "romanian_deadlift_db", "rdl_bw"]
LEG_CURL = ["seated_leg_curl", "lying_leg_curl", "slider_leg_curl", "nordic_band"]
CALF = ["standing_calf_raise", "seated_calf_raise", "single_leg_calf_raise"]
CORE_AE = ["dead_bug", "plank"]
LATERAL = ["dumbbell_lateral_raise", "cable_lateral_raise", "band_lateral_raise"]
CURL = ["dumbbell_curl", "barbell_curl", "cable_curl", "band_curl"]
TRI = ["rope_pushdown", "cable_pushdown_bar", "seated_db_overhead_extension", "bench_dip", "bodyweight_triceps_extension"]

TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "T01", "name": "Старт: фулбоди A/B",
        "summary": "Две тренировки на всё тело по очереди. Осваиваем технику, вес не форсируем.",
        "principle": "план новичка по рекомендациям ACSM 2026 и NSCA",
        "goals": ["strength", "strength_mass", "mass", "weight_loss", "general"], "levels": ["beginner"],
        "days": [2, 3], "inventory": ["gym", "home_barbell", "dumbbells"], "session": [45, 60],
        "progression": "double", "engine_ready": True, "fallback": None,
        "phases": [
            {"weeks": "1–2", "scheme": "1–2 × 10–15, запас 3–4, вес не форсировать"},
            {"weeks": "3–6", "scheme": "2–3 × 8–12, запас 2–3, двойная прогрессия"},
            {"weeks": "7–12", "scheme": "3 × 6–10 в базовых, запас 1–3; затем программа по цели"},
        ],
        "days_spec": [
            D("A", S(SQ, "main", (2, 3), (8, 12), ["goblet_squat", "leg_press_45", "bodyweight_squat"], (2, 3)),
              S(HPU, "secondary", (2, 3), (8, 12), ["machine_chest_press", "dumbbell_bench_press", "push_up"], (2, 3)),
              S(VPL, "secondary", (2, 3), (8, 12), ["lat_pulldown_wide", "band_lat_pulldown", "one_arm_dumbbell_row"], (2, 3)),
              S(HG, "secondary", (2, 3), (8, 12), ["romanian_deadlift_db", "back_extension_45", "rdl_bw"], (2, 3)),
              S(CAE, "accessory", 2, (20, 40), CORE_AE, (2, 3), prog="time")),
            D("B", S(SQ, "main", (2, 3), (8, 12), ["leg_press_45", "split_squat", "bodyweight_squat"], (2, 3)),
              S(VPU, "secondary", (2, 3), (8, 12), ["machine_shoulder_press", "dumbbell_shoulder_press_seated", "pike_push_up"], (2, 3)),
              S(HPL, "secondary", (2, 3), (8, 12), ["seated_cable_row", "chest_supported_dumbbell_row", "door_towel_row"], (2, 3)),
              S(KF, "accessory", (2, 3), (8, 12), ["seated_leg_curl", "slider_leg_curl"], (2, 3)),
              S(CAR, "accessory", 2, (8, 12), ["pallof_press", "side_plank"], (2, 3))),
        ],
    },
    {
        "id": "T02", "name": "Линейная 3×5 A/B",
        "summary": "Три базовых движения за тренировку, вес растёт почти каждую сессию.",
        "principle": "линейные программы для новичков (рекомендации r/Fitness, GreySkull LP, StrongLifts)",
        "goals": ["strength", "strength_mass"], "levels": ["beginner"], "days": [2, 3],
        "inventory": ["gym", "home_barbell"], "session": [45, 75],
        "progression": "linear", "engine_ready": False, "fallback": "T09",
        "rules": {"gain": "каждую сессию: низ +2,5 кг (становая в начале +5), верх +1,25–2,5",
                  "stall": "сумма повторений меньше 15 → −10%; два сброса на движении → T03 или T04",
                  "rest_min": [2, 3], "duration": "не дольше трёх месяцев"},
        "days_spec": [
            D("A", S(SQ, "main", 3, (5, 5), ["back_squat_high_bar", "goblet_squat", "bodyweight_squat"], (1, 2), prog="linear"),
              S(HPU, "main", 3, (5, 5), BENCH_MAIN, (1, 2), prog="linear"),
              S(HPL, "main", 3, (5, 5), ["barbell_bent_over_row", "one_arm_dumbbell_row", "door_towel_row"], (1, 2), prog="linear"),
              S(RD, "accessory", (2, 3), (8, 12), ["face_pull", "band_face_pull", "bent_over_reverse_fly"], optional="strength_mass"),
              S(EF, "accessory", (2, 3), (8, 12), CURL, optional="strength_mass"),
              S(CAE, "accessory", (2, 3), (20, 40), ["plank", "dead_bug"], prog="time", optional="strength_mass")),
            D("B", S(VPL, "main", 3, (5, 5), ["chin_up", "lat_pulldown_reverse", "band_lat_pulldown", "door_towel_row"], (1, 2), prog="linear"),
              S(VPU, "main", 3, (5, 5), ["barbell_overhead_press", "dumbbell_shoulder_press_seated", "pike_push_up"], (1, 2), prog="linear"),
              S(HG, "main", 3, (5, 5), ["deadlift_conventional", "romanian_deadlift_bb", "romanian_deadlift_db", "rdl_bw"], (1, 2), prog="linear"),
              S(EE, "accessory", (2, 3), (8, 12), TRI, optional="strength_mass"),
              S(SHI, "accessory", (2, 3), (8, 12), LATERAL, optional="strength_mass"),
              S(CFL, "accessory", (2, 3), (10, 15), ["crunch", "reverse_crunch"], optional="strength_mass")),
        ],
    },
    {
        "id": "T03", "name": "Тиры: тяжёлый, объёмный, подсобка",
        "summary": "Четыре тренировки в ротации: тяжёлое движение, объёмное и лёгкая подсобка.",
        "principle": "тировая прогрессия (GZCL-подобная)",
        "goals": ["strength", "strength_mass"], "levels": ["beginner", "intermediate"], "days": [3, 4],
        "inventory": ["gym", "home_barbell"], "session": [60, 75],
        "progression": "stages", "engine_ready": False, "fallback": "T07",
        "stages": {"T1": ["5×3+", "6×2+", "10×1+"], "T2": ["3×10", "3×8", "3×6"], "T3": ["3×15+"]},
        "days_spec": [
            D("Тренировка 1", S(SQ, "main", 5, (3, 3), SQUAT_MAIN, (1, 2), prog="stages", tier="T1"),
              S(HPU, "secondary", 3, (6, 10), BENCH_MAIN, (1, 2), prog="stages", tier="T2"),
              S(VPL, "accessory", 3, (15, 15), PULL_V, prog="stages", tier="T3")),
            D("Тренировка 2", S(VPU, "main", 5, (3, 3), OHP, (1, 2), prog="stages", tier="T1"),
              S(HG, "secondary", 3, (6, 10), HINGE_MAIN, (1, 2), prog="stages", tier="T2"),
              S(HPL, "accessory", 3, (15, 15), ["one_arm_dumbbell_row", "seated_cable_row", "door_towel_row"], prog="stages", tier="T3")),
            D("Тренировка 3", S(HPU, "main", 5, (3, 3), BENCH_MAIN, (1, 2), prog="stages", tier="T1"),
              S(SQ, "secondary", 3, (6, 10), SQUAT_MAIN, (1, 2), prog="stages", tier="T2"),
              S(VPL, "accessory", 3, (15, 15), PULL_V, prog="stages", tier="T3")),
            D("Тренировка 4", S(HG, "main", 5, (3, 3), HINGE_MAIN, (1, 2), prog="stages", tier="T1"),
              S(VPU, "secondary", 3, (6, 10), OHP, (1, 2), prog="stages", tier="T2"),
              S(HPL, "accessory", 3, (15, 15), ["one_arm_dumbbell_row", "seated_cable_row", "door_towel_row"], prog="stages", tier="T3")),
        ],
    },
    {
        "id": "T04", "name": "Трёхнедельные волны: базовый",
        "summary": "Два базовых движения в день, три недели нагрузки по процентам от тренировочного максимума.",
        "principle": "волновая прогрессия с тренировочным максимумом 90% от расчётного максимума",
        "goals": ["strength", "strength_mass"], "levels": ["intermediate"], "days": [3],
        "inventory": ["gym", "home_barbell"], "session": [60, 60],
        "progression": "waves", "engine_ready": False, "fallback": "T07",
        "week_scheme": [["65/75/85%", "5 5 5+"], ["70/80/90%", "3 3 3+"], ["75/85/95%", "5 3 1+"]],
        "days_spec": [
            D("День 1", S(SQ, "main", 3, (5, 5), SQUAT_MAIN, (1, 2), prog="waves"), S(HPU, "main", 3, (5, 5), BENCH_MAIN, (1, 2), prog="waves"),
              S(HPL, "accessory", (3, 5), (8, 12), ROW_MAIN), S(CAE, "accessory", 3, (20, 40), CORE_AE, prog="time")),
            D("День 2", S(HG, "main", 3, (5, 5), HINGE_MAIN, (1, 2), prog="waves"), S(VPU, "main", 3, (5, 5), OHP, (1, 2), prog="waves"),
              S(VPL, "accessory", (3, 5), (8, 12), PULL_V), S(LU, "accessory", 3, (8, 12), ["split_squat", "reverse_lunge", "step_up"])),
            D("День 3", S(HPU, "main", 3, (5, 5), BENCH_MAIN, (1, 2), prog="waves"), S(SQ, "main", 3, (5, 5), SQUAT_MAIN, (1, 2), prog="waves"),
              S(HPL, "accessory", (3, 5), (8, 12), ROW_MAIN), S(CFL, "accessory", 3, (10, 15), ["crunch", "reverse_crunch"])),
        ],
    },
    {
        "id": "T05", "name": "Волны плюс объём 5×10",
        "summary": "Четыре тренировки: основное движение по волнам и объёмная работа 5×10 на нём же.",
        "principle": "волны плюс дополнительный объём на том же движении",
        "goals": ["strength", "strength_mass"], "levels": ["intermediate", "advanced"], "days": [3, 4],
        "inventory": ["gym", "home_barbell"], "session": [60, 75],
        "progression": "waves", "engine_ready": False, "fallback": "T07",
        "days_spec": [
            D("День 1", S(SQ, "main", 3, (5, 5), SQUAT_MAIN, (1, 2), prog="waves"), S(SQ, "secondary", 5, (10, 10), SQUAT_MAIN, (2, 3), prog="waves"),
              S(VPL, "accessory", (4, 5), (10, 15), PULL_V), S(CFL, "accessory", 3, (10, 15), ["crunch", "reverse_crunch"])),
            D("День 2", S(HPU, "main", 3, (5, 5), BENCH_MAIN, (1, 2), prog="waves"), S(HPU, "secondary", 5, (10, 10), BENCH_MAIN, (2, 3), prog="waves"),
              S(HPL, "accessory", (4, 5), (10, 15), ROW_MAIN), S(CAE, "accessory", 3, (20, 40), CORE_AE, prog="time")),
            D("День 3", S(HG, "main", 3, (5, 5), HINGE_MAIN, (1, 2), prog="waves"), S(HG, "secondary", 5, (10, 10), ["romanian_deadlift_bb", "romanian_deadlift_db", "rdl_bw"], (2, 3), prog="waves"),
              S(VPL, "accessory", (4, 5), (10, 15), PULL_V), S(CFL, "accessory", 3, (10, 15), ["crunch", "reverse_crunch"])),
            D("День 4", S(VPU, "main", 3, (5, 5), OHP, (1, 2), prog="waves"), S(VPU, "secondary", 5, (10, 10), OHP, (2, 3), prog="waves"),
              S(HPL, "accessory", (4, 5), (10, 15), ROW_MAIN), S(CAE, "accessory", 3, (20, 40), CORE_AE, prog="time")),
        ],
    },
    {
        "id": "T06", "name": "Недельная волна: объём, лёгкий, интенсивность",
        "summary": "Три дня недели с разной нагрузкой: объёмный, лёгкий и рекордный.",
        "principle": "недельная периодизация (объём, восстановление, интенсивность)",
        "goals": ["strength"], "levels": ["intermediate"], "days": [3],
        "inventory": ["gym", "home_barbell"], "session": [60, 75],
        "progression": "weekly_wave", "engine_ready": False, "fallback": "T09",
        "days_spec": [
            D("Понедельник (объём)", S(SQ, "main", 5, (5, 5), SQUAT_MAIN, (1, 2), prog="weekly_wave"),
              S(HPU, "main", 5, (5, 5), BENCH_MAIN, (1, 2), prog="weekly_wave", alternates_with=VPU)),
            D("Среда (лёгкий)", S(SQ, "main", 2, (5, 5), SQUAT_MAIN, (3, 4), prog="weekly_wave"), S(VPU, "secondary", 3, (5, 5), OHP, (3, 4)),
              S(VPL, "secondary", 3, (6, 10), ["pull_up", "chin_up", "lat_pulldown_wide", "band_lat_pulldown", "door_towel_row"]),
              S(HG, "accessory", 3, (8, 12), ["back_extension_45", "romanian_deadlift_db", "rdl_bw"])),
            D("Пятница (интенсивность)", S(SQ, "main", 1, (5, 5), SQUAT_MAIN, (0, 1), prog="weekly_wave"),
              S(HPU, "main", 1, (5, 5), BENCH_MAIN, (0, 1), prog="weekly_wave"), S(HG, "main", 1, (5, 5), HINGE_MAIN, (1, 2), prog="weekly_wave")),
        ],
    },
    {
        "id": "T07", "name": "Верх/низ: сила и гипертрофия",
        "summary": "Четыре дня: два силовых и два на объём, верх и низ чередуются.",
        "principle": "верх/низ с силовыми и гипертрофийными днями (PHUL-подобный)",
        "goals": ["strength_mass", "mass", "strength"], "levels": ["intermediate"], "days": [4],
        "inventory": ["gym"], "session": [60, 75],
        "progression": "double", "engine_ready": True, "fallback": None,
        "days_spec": [
            D("Верх-сила", S(HPU, "main", (3, 4), (3, 5), BENCH_MAIN, (1, 2)), S(HPL, "main", (3, 4), (3, 5), ["barbell_bent_over_row", "seated_cable_row", "one_arm_dumbbell_row"], (1, 2)),
              S(VPU, "secondary", 3, (6, 10), OHP, (1, 3)), S(VPL, "secondary", 3, (6, 10), PULL_V, (1, 3)),
              S(EF, "accessory", (2, 3), (6, 10), CURL), S(EE, "accessory", (2, 3), (6, 10), TRI)),
            D("Низ-сила", S(SQ, "main", (3, 4), (3, 5), SQUAT_MAIN, (1, 2)), S(HG, "main", (3, 4), (3, 5), HINGE_MAIN, (1, 2)),
              S(SQ, "secondary", 3, (6, 10), ["leg_press_45", "hack_squat", "goblet_squat"], (1, 3)), S(KF, "secondary", 3, (6, 10), LEG_CURL, (1, 3)),
              S(CA, "accessory", (3, 4), (6, 10), CALF)),
            D("Верх-гипертрофия", S(HPU, "main", (3, 4), (8, 12), ["incline_dumbbell_press", "dumbbell_bench_press", "push_up"]), S(CHI, "secondary", 3, (8, 12), ["cable_crossover", "dumbbell_fly", "band_fly"]),
              S(HPL, "secondary", (3, 4), (8, 12), ["seated_cable_row", "chest_supported_dumbbell_row", "door_towel_row"]), S(HPL, "secondary", 3, (8, 12), ["one_arm_dumbbell_row", "single_arm_cable_row"]),
              S(SHI, "accessory", 3, (10, 15), LATERAL), S(EF, "accessory", 3, (8, 12), CURL), S(EE, "accessory", 3, (8, 12), TRI)),
            D("Низ-гипертрофия", S(SQ, "main", (3, 4), (10, 15), ["front_squat", "leg_press_45", "goblet_squat"]), S(LU, "secondary", 3, (10, 15), ["bulgarian_split_squat", "split_squat", "reverse_lunge"]),
              S(KE, "accessory", 3, (10, 15), ["leg_extension", "reverse_nordic"]), S(KF, "accessory", 3, (10, 15), LEG_CURL), S(CA, "accessory", 3, (10, 15), CALF)),
        ],
    },
    {
        "id": "T08", "name": "Верх/низ: масса",
        "summary": "Четыре дня на рост мышц: около 10–12 подходов на мышцу в неделю и двойная прогрессия.",
        "principle": "верх/низ для гипертрофии с ориентирами по объёму Renaissance Periodization",
        "goals": ["mass", "weight_loss"], "levels": ["beginner", "intermediate"], "days": [4],
        "inventory": ["gym", "dumbbells"], "session": [60, 60],
        "progression": "double", "engine_ready": True, "fallback": None,
        "days_spec": [
            D("Верх A", S(HPU, "main", 3, (6, 10), ["barbell_bench_press", "dumbbell_bench_press", "dumbbell_floor_press", "push_up"], (1, 3)),
              S(VPL, "secondary", 3, (8, 12), PULL_V, (1, 3)), S(VPU, "secondary", (2, 3), (8, 12), OHP, (1, 3)),
              S(HPL, "secondary", 3, (8, 12), ROW_MAIN, (1, 3)), S(SHI, "accessory", (2, 3), (12, 20), LATERAL, (0, 1)),
              S(EE, "accessory", 2, (10, 15), TRI, (0, 1))),
            D("Низ A", S(SQ, "main", 3, (6, 10), ["back_squat_high_bar", "hack_squat", "goblet_squat", "bodyweight_squat"], (1, 3)),
              S(HG, "secondary", 3, (8, 10), ["romanian_deadlift_bb", "romanian_deadlift_db", "rdl_bw"], (1, 3)),
              S(LU, "secondary", (2, 3), (10, 12), ["split_squat", "reverse_lunge", "step_up"], (1, 3)), S(KF, "accessory", 3, (10, 15), LEG_CURL, (0, 1)),
              S(CA, "accessory", 3, (10, 15), CALF, (0, 1))),
            D("Верх B", S(HPU, "main", 3, (8, 12), ["incline_dumbbell_press", "barbell_incline_bench_press", "dumbbell_floor_press", "push_up"], (1, 3)),
              S(HPL, "secondary", 3, (8, 12), ROW_MAIN, (1, 3)), S(VPL, "secondary", 3, (10, 12), PULL_V, (1, 3)),
              S(CHI, "accessory", 2, (12, 15), ["cable_crossover", "dumbbell_fly", "band_fly"], (0, 1)), S(RD, "accessory", (2, 3), (15, 20), ["face_pull", "band_face_pull", "bent_over_reverse_fly"], (0, 1)),
              S(EF, "accessory", (2, 3), (10, 15), CURL, (0, 1))),
            D("Низ B", S(SQ, "main", 3, (10, 15), ["leg_press_45", "goblet_squat", "bodyweight_squat"], (1, 3)),
              S(HE, "secondary", 3, (8, 12), ["hip_thrust_bb", "hip_thrust_db", "glute_bridge_bw"], (1, 3)),
              S(KE, "accessory", (2, 3), (12, 15), ["leg_extension", "reverse_nordic"], (0, 1)), S(KF, "accessory", (2, 3), (10, 15), LEG_CURL, (0, 1)),
              S(CFL, "accessory", (2, 3), (10, 15), ["cable_crunch", "crunch", "reverse_crunch"])),
        ],
    },
    {
        "id": "T09", "name": "Фулбоди ×3: масса",
        "summary": "Три тренировки на всё тело, каждая мышца работает не реже двух раз в неделю.",
        "principle": "фулбоди с частотой не меньше двух в неделю (Stronger By Science)",
        "goals": ["mass", "strength_mass", "weight_loss", "strength"], "levels": ["beginner", "intermediate"], "days": [3],
        "inventory": ["gym", "home_barbell", "dumbbells"], "session": [60, 60],
        "progression": "double", "engine_ready": True, "fallback": None,
        "days_spec": [
            D("A", S(SQ, "main", 3, (6, 10), SQUAT_MAIN, (1, 3)), S(HPU, "main", 3, (6, 10), BENCH_MAIN, (1, 3)),
              S(HPL, "secondary", 3, (8, 12), ROW_MAIN, (1, 3)), S(KF, "accessory", 2, (10, 15), LEG_CURL), S(SHI, "accessory", 2, (12, 20), LATERAL)),
            D("B", S(HG, "main", 3, (6, 10), ["romanian_deadlift_bb", "trap_bar_deadlift", "romanian_deadlift_db", "rdl_bw"], (1, 3)), S(VPU, "main", 3, (8, 10), OHP, (1, 3)),
              S(VPL, "secondary", 3, (8, 12), PULL_V, (1, 3)), S(LU, "accessory", 2, (10, 12), ["split_squat", "reverse_lunge", "step_up"]), S(EF, "accessory", 2, (10, 15), CURL)),
            D("C", S(SQ, "main", 3, (8, 12), ["leg_press_45", "front_squat", "goblet_squat", "bodyweight_squat"], (1, 3)), S(HPU, "secondary", 3, (8, 12), ["incline_dumbbell_press", "barbell_incline_bench_press", "dumbbell_floor_press", "push_up"], (1, 3)),
              S(HPL, "secondary", 3, (8, 12), ["seated_cable_row", "chest_supported_dumbbell_row", "one_arm_dumbbell_row", "door_towel_row"], (1, 3)),
              S(HE, "accessory", (2, 3), (8, 12), ["hip_thrust_bb", "hip_thrust_db", "glute_bridge_bw"]), S(EE, "accessory", 2, (10, 15), TRI), S(CFL, "accessory", 2, (10, 15), ["cable_crunch", "crunch"])),
        ],
    },
    {
        "id": "T10", "name": "Верх/низ плюс тяни/толкай/ноги",
        "summary": "Пять дней: два силовых и три на объём. Для хорошо восстанавливающихся.",
        "principle": "гибрид силовых и гипертрофийных дней (PHAT-подобный), сессия урезана до 5–6 слотов",
        "goals": ["strength_mass", "mass", "strength"], "levels": ["intermediate", "advanced"], "days": [5, 6],
        "inventory": ["gym"], "session": [60, 75],
        "progression": "double", "engine_ready": True, "fallback": None,
        "days_spec": [
            D("1 Верх-сила", S(HPU, "main", 3, (3, 5), BENCH_MAIN, (1, 2)), S(HPL, "main", 3, (3, 5), ["barbell_bent_over_row", "seated_cable_row", "one_arm_dumbbell_row"], (1, 2)),
              S(VPU, "secondary", (2, 3), (6, 8), OHP, (1, 2))),
            D("2 Низ-сила", S(SQ, "main", 3, (3, 5), SQUAT_MAIN, (1, 2)), S(HG, "main", (2, 3), (3, 5), HINGE_MAIN, (1, 2)), S(KF, "secondary", 3, (6, 10), LEG_CURL, (1, 2))),
            D("3 Тяни", S(VPL, "main", 3, (8, 12), PULL_V), S(HPL, "main", 3, (10, 15), ["seated_cable_row", "chest_supported_dumbbell_row", "door_towel_row"]),
              S(RD, "accessory", 3, (15, 20), ["face_pull", "band_face_pull", "bent_over_reverse_fly"]), S(EF, "accessory", 3, (10, 15), CURL)),
            D("4 Ноги", S(SQ, "main", 3, (8, 15), ["hack_squat", "leg_press_45", "goblet_squat"]), S(HG, "secondary", 3, (8, 12), ["romanian_deadlift_bb", "romanian_deadlift_db", "rdl_bw"]),
              S(LU, "secondary", (2, 3), (10, 15), ["bulgarian_split_squat", "split_squat", "reverse_lunge"]), S(KE, "accessory", 3, (12, 20), ["leg_extension", "reverse_nordic"]),
              S(KF, "accessory", 3, (10, 15), LEG_CURL), S(CA, "accessory", 3, (10, 20), CALF)),
            D("5 Толкай", S(HPU, "main", 3, (8, 12), ["incline_dumbbell_press", "dumbbell_bench_press", "push_up"]), S(HPU, "secondary", 3, (8, 15), ["machine_chest_press", "chest_dip", "dumbbell_floor_press", "push_up"]),
              S(SHI, "accessory", (3, 4), (12, 20), LATERAL), S(EE, "accessory", 3, (10, 15), TRI)),
        ],
    },
    {
        "id": "T11", "name": "Тяни/толкай/ноги ×2",
        "summary": "Шесть дней: три типа тренировок дважды в неделю. Для тех, кто восстанавливается быстро.",
        "principle": "тяни/толкай/ноги с линейной прогрессией в базовых",
        "goals": ["mass", "strength_mass"], "levels": ["beginner", "intermediate"], "days": [6],
        "inventory": ["gym"], "session": [60, 75],
        "progression": "double", "engine_ready": True, "fallback": None,
        "days_spec": [
            D("Тяни", S(HG, "main", 1, (5, 5), ["deadlift_conventional", "romanian_deadlift_bb", "romanian_deadlift_db"], (1, 2), alternates_with=HPL), S(VPL, "secondary", 3, (8, 12), PULL_V),
              S(HPL, "secondary", 3, (8, 12), ["seated_cable_row", "chest_supported_dumbbell_row", "door_towel_row"]), S(RD, "accessory", 5, (15, 20), ["face_pull", "band_face_pull", "bent_over_reverse_fly"]),
              S(EF, "accessory", 4, (8, 12), ["hammer_curl", "dumbbell_curl", "cable_curl"])),
            D("Толкай", S(HPU, "main", 4, (5, 5), BENCH_MAIN, (1, 2), alternates_with=VPU), S(VPU, "secondary", 3, (8, 12), OHP),
              S(HPU, "secondary", 3, (8, 12), ["incline_dumbbell_press", "dumbbell_bench_press", "push_up"]), S(EE, "accessory", 3, (8, 12), TRI), S(SHI, "accessory", 3, (15, 20), LATERAL)),
            D("Ноги", S(SQ, "main", 2, (5, 5), SQUAT_MAIN, (1, 2)), S(HG, "secondary", 3, (8, 12), ["romanian_deadlift_bb", "romanian_deadlift_db", "rdl_bw"]),
              S(SQ, "secondary", 3, (8, 12), ["leg_press_45", "hack_squat", "goblet_squat"]), S(KF, "accessory", 3, (8, 12), LEG_CURL), S(CA, "accessory", 5, (8, 12), CALF)),
        ],
    },
    {
        "id": "T12", "name": "Сплит по группам мышц",
        "summary": "Каждая группа мышц один раз в неделю. Только по прямой просьбе: частота ниже оптимальной.",
        "principle": "классический сплит по группам мышц",
        "goals": ["mass"], "levels": ["intermediate", "advanced"], "days": [3, 4, 5],
        "inventory": ["gym"], "session": [60, 75],
        "progression": "double", "engine_ready": True, "fallback": None, "on_request_only": True,
        "warning": "Частота один раз в неделю на мышцу. Сплит утомляет сильнее; при равном объёме фулбоди не хуже. Новичкам не подходит.",
        "days_spec": [
            D("Грудь и бицепс", S(HPU, "main", 3, (8, 12), BENCH_MAIN), S(HPU, "secondary", 3, (8, 12), ["incline_dumbbell_press", "dumbbell_bench_press", "push_up"]),
              S(CHI, "accessory", 3, (10, 15), ["cable_crossover", "dumbbell_fly", "band_fly"]), S(EF, "accessory", 3, (8, 12), CURL)),
            D("Спина и трицепс", S(VPL, "main", 3, (8, 12), PULL_V), S(HPL, "main", 3, (8, 12), ROW_MAIN),
              S(HPL, "secondary", 3, (8, 12), ["seated_cable_row", "single_arm_cable_row", "door_towel_row"]), S(EE, "accessory", 3, (8, 12), TRI)),
            D("Ноги и ягодицы", S(SQ, "main", 4, (8, 12), SQUAT_MAIN), S(HG, "secondary", 3, (8, 12), ["romanian_deadlift_bb", "romanian_deadlift_db", "rdl_bw"]),
              S(HE, "secondary", 3, (8, 12), ["hip_thrust_bb", "hip_thrust_db", "glute_bridge_bw"]), S(KF, "accessory", 3, (10, 12), LEG_CURL), S(CA, "accessory", 3, (10, 15), CALF)),
            D("Плечи и трапеции", S(VPU, "main", 3, (8, 12), OHP), S(SHI, "secondary", 3, (10, 15), LATERAL),
              S(RD, "accessory", 3, (12, 20), ["face_pull", "band_face_pull", "bent_over_reverse_fly"]), S(SC, "accessory", 3, (10, 15), ["dumbbell_shrug", "barbell_shrug"])),
        ],
    },
    {
        "id": "T13", "name": "Минимум: 2 × 30 минут",
        "summary": "Две короткие тренировки в неделю суперсетами: самое необходимое при нехватке времени.",
        "principle": "минимальная эффективная доза (Iversen 2021, Nuzzo 2024, ACSM 2026)",
        "goals": ["strength", "strength_mass", "mass", "weight_loss", "general", "return"],
        "levels": ["beginner", "intermediate", "advanced"], "days": [2, 3, 4, 5, 6],
        "inventory": ["gym", "home_barbell", "dumbbells", "bodyweight", "kettlebell"], "session": [30, 30],
        "progression": "double", "engine_ready": True, "fallback": None,
        "warning": "Около 4–8 подходов на мышцу в неделю. Для цели «Масса» это нижняя граница.",
        "days_spec": [
            D("A", S(SQ, "main", (2, 3), (6, 12), ["goblet_squat", "leg_press_45", "back_squat_high_bar", "bodyweight_squat"], (1, 2), superset="1"),
              S(HPL, "main", (2, 3), (6, 12), ROW_MAIN, (1, 2), superset="1"),
              S(HPU, "main", (2, 3), (6, 12), ["barbell_bench_press", "dumbbell_bench_press", "dumbbell_floor_press", "push_up"], (1, 2), superset="2"),
              S(VPL, "main", (2, 3), (6, 12), PULL_V, (1, 2), superset="2"),
              S(CFL, "accessory", 2, (10, 15), ["crunch", "reverse_crunch"])),
            D("B", S(HG, "main", (2, 3), (6, 12), ["romanian_deadlift_bb", "trap_bar_deadlift", "romanian_deadlift_db", "hip_thrust_bw", "rdl_bw"], (1, 2), superset="1"),
              S(VPU, "main", (2, 3), (6, 12), OHP, (1, 2), superset="1"),
              S(LU, "main", (2, 3), (6, 12), ["split_squat", "reverse_lunge", "step_up"], (1, 2), superset="2"),
              S(HPL, "main", (2, 3), (6, 12), ["seated_cable_row", "one_arm_dumbbell_row", "door_towel_row"], (1, 2), superset="2"),
              S(KF, "accessory", 2, (10, 15), LEG_CURL)),
        ],
    },
    {
        "id": "T14", "name": "Возвращение",
        "summary": "Мягкий вход после перерыва: объём 50–60% прежнего, запас 3–4 повтора, без отказа первые две недели.",
        "principle": "восстановление после детренированности (Stronger By Science), выбор веса по скорости",
        "goals": ["return", "strength", "strength_mass", "mass", "weight_loss", "general"],
        "levels": ["beginner", "intermediate", "advanced"], "days": [2, 3, 4, 5, 6],
        "inventory": ["gym", "home_barbell", "dumbbells", "bodyweight", "kettlebell"], "session": [45, 60],
        "progression": "double", "engine_ready": True, "fallback": None,
        "rules": {"duration_weeks": [2, 6], "volume": "50–60% прежнего, +1 подход в неделю", "rir": "3–4 первые 2 недели, затем 2–3",
                  "exit": "через 4–6 недель или при ~90% прежних рабочих весов → программа по цели",
                  "screening": "перерыв больше 2–3 месяцев → повторный скрининг; после травмы — допуск специалиста"},
        "days_spec": [
            D("A", S(SQ, "main", 2, (10, 12), ["goblet_squat", "leg_press_45", "bodyweight_squat"], (3, 4)),
              S(HPU, "secondary", 2, (10, 12), ["machine_chest_press", "dumbbell_bench_press", "push_up"], (3, 4)),
              S(VPL, "secondary", 2, (10, 12), ["lat_pulldown_wide", "band_lat_pulldown", "one_arm_dumbbell_row", "door_towel_row"], (3, 4)),
              S(HG, "secondary", 2, (10, 12), ["romanian_deadlift_db", "back_extension_45", "rdl_bw"], (3, 4)),
              S(CAE, "accessory", 2, (20, 40), CORE_AE, prog="time")),
            D("B", S(SQ, "main", 2, (10, 12), ["leg_press_45", "split_squat", "bodyweight_squat"], (3, 4)),
              S(VPU, "secondary", 2, (10, 12), ["machine_shoulder_press", "dumbbell_shoulder_press_seated", "pike_push_up"], (3, 4)),
              S(HPL, "secondary", 2, (10, 12), ["seated_cable_row", "chest_supported_dumbbell_row", "door_towel_row"], (3, 4)),
              S(KF, "accessory", 2, (10, 12), ["seated_leg_curl", "slider_leg_curl"], (3, 4)),
              S(CAR, "accessory", 2, (8, 12), ["pallof_press", "side_plank"])),
        ],
    },
    {
        "id": "T15", "name": "Гантели дома A/B",
        "summary": "Домашняя программа на гантелях: скамья, резина и турник по желанию.",
        "principle": "домашняя программа на гантелях (Dumbbell Stopgap)",
        "goals": ["mass", "strength_mass", "general", "weight_loss", "return"], "levels": ["beginner", "intermediate"],
        "days": [3, 4], "inventory": ["dumbbells"], "session": [45, 45],
        "progression": "double", "engine_ready": True, "fallback": None,
        "warning": "Для цели «максимальная сила» без тяжёлых весов результат ниже: гантели ограничивают нагрузку.",
        "days_spec": [
            D("A", S(LU, "main", 3, (8, 12), ["bulgarian_split_squat", "reverse_lunge", "split_squat"]), S(HPU, "main", 3, (8, 12), ["dumbbell_bench_press", "dumbbell_floor_press", "push_up"]),
              S(HG, "secondary", 3, (8, 12), ["romanian_deadlift_db", "rdl_bw"]), S(CAE, "accessory", 3, (20, 40), ["plank", "dead_bug"], prog="time"),
              S(SHI, "accessory", 3, (10, 20), LATERAL, optional="mass"), S(EF, "accessory", 3, (10, 20), ["dumbbell_curl", "hammer_curl"], optional="mass")),
            D("B", S(LU, "main", 3, (8, 12), ["split_squat", "reverse_lunge", "walking_lunge"]), S(VPU, "main", 3, (8, 12), ["dumbbell_shoulder_press_seated", "dumbbell_shoulder_press_standing", "pike_push_up"]),
              S(HPL, "secondary", 3, (8, 12), ["two_arm_dumbbell_row", "one_arm_dumbbell_row"]), S(CAE, "accessory", 3, (20, 40), ["plank", "dead_bug"], prog="time"),
              S(HE, "accessory", 3, (8, 12), ["hip_thrust_db", "glute_bridge_bw"], optional="mass"), S(KF, "accessory", 3, (8, 12), ["slider_leg_curl", "db_leg_curl"], optional="mass"),
              S(EE, "accessory", 3, (10, 15), ["seated_db_overhead_extension", "single_arm_overhead_extension", "dumbbell_kickback"], optional="mass")),
        ],
    },
    {
        "id": "T16", "name": "Лестницы с собственным весом",
        "summary": "Три дня парами упражнений-лестниц: от простых вариантов к сложным без снарядов.",
        "principle": "лестницы прогрессий калистеники (рекомендованная рутина r/bodyweightfitness)",
        "goals": ["general", "strength_mass", "mass", "weight_loss", "return"], "levels": ["beginner", "intermediate"],
        "days": [3, 4, 5, 6], "inventory": ["bodyweight"], "session": [45, 60],
        "progression": "ladder", "engine_ready": False, "fallback": "T09",
        "rules": {"progress": "3×5 → +1 повторение за сессию → 3×8 → следующая ступень; удержания до 3×30 с", "rest_s": [60, 90]},
        "days_spec": [
            D("Тренировка", S(VPL, "main", 3, (5, 8), ["scapular_pull_up", "negative_pull_up", "chin_up", "pull_up", "door_towel_row", "inverted_row"], ladder="L_PULL_V", prog="ladder"),
              S(SQ, "main", 3, (8, 15), ["bodyweight_squat", "split_squat", "bulgarian_split_squat", "skater_squat"], ladder="L_SQUAT", prog="ladder"),
              S(HPU, "main", 3, (5, 8), ["triceps_dip", "bench_dip", "push_up"], ladder="L_DIP", prog="ladder"),
              S(HG, "main", 3, (8, 12), ["rdl_bw", "single_leg_rdl", "nordic_band"], ladder="L_HINGE", prog="ladder"),
              S(HPL, "main", 3, (5, 8), ["inverted_row", "ring_row", "door_towel_row", "table_row"], ladder="L_PULL_H", prog="ladder"),
              S(HPU, "main", 3, (5, 8), ["push_up", "incline_push_up", "knee_push_up", "wall_push_up"], ladder="L_PUSH_H", prog="ladder"),
              S(CAE, "accessory", 3, (20, 30), ["dead_bug", "plank"], ladder="L_ANTI_EXT", prog="ladder"),
              S(CAR, "accessory", 3, (8, 12), ["bird_dog", "side_plank"], ladder="L_ANTI_ROT", prog="ladder"),
              S(CEX, "accessory", 3, (20, 30), ["arch_hold"], ladder="L_EXT", prog="ladder")),
        ],
    },
    {
        "id": "T17", "name": "Гиревой минимум: махи и турецкий подъём",
        "summary": "Короткие сессии с одной гирей: махи и турецкий подъём на время.",
        "principle": "гиревая структура «махи плюс подъём» (в духе Simple & Sinister, без использования названия)",
        "goals": ["general", "strength_mass", "weight_loss", "mass"], "levels": ["beginner", "intermediate"],
        "days": [2, 3, 4, 5, 6], "inventory": ["kettlebell"], "session": [20, 30],
        "progression": "time", "engine_ready": False, "fallback": "T19",
        "days_spec": [
            D("Сессия", S(KB, "accessory", 1, (5, 8), ["kb_halo", "goblet_squat", "kb_deadlift"], prog="warmup"),
              S(HG, "main", 10, (10, 10), ["kb_swing_1h", "kettlebell_swing", "kb_deadlift"], prog="time", format="10 махов каждые 30 секунд"),
              S(KB, "main", 10, (1, 1), ["kb_tgu", "kb_halo", "kb_deadlift"], prog="time", format="один подъём в минуту")),
        ],
    },
    {
        "id": "T18", "name": "Похудение: удержать силу",
        "summary": "Силовая часть сохраняет мышцы, кардио добавляет расход энергии. Дефицит калорий не назначается.",
        "principle": "силовая тренировка в дефиците и разнесение с кардио (Murphy & Koehler, Schumann, WHO 2020)",
        "goals": ["weight_loss"], "levels": ["beginner", "intermediate", "advanced"], "days": [2, 3, 4, 5, 6],
        "inventory": ["gym", "home_barbell", "dumbbells", "bodyweight", "kettlebell"], "session": [30, 60],
        "progression": "double", "engine_ready": True, "fallback": None,
        "base_by_days": {"2": "T13", "3": "T09", "4": "T08", "5": "T08", "6": "T08"},
        "base_home": {"dumbbells": "T15", "bodyweight": "T16", "kettlebell": "T19"},
        "cardio": {"zone2": "2–3 раза по 30–45 минут", "intervals": "1 интервальная в неделю",
                   "rule": "интервалы не ставить перед тяжёлыми ногами, разносить минимум на 3 часа"},
        "warning": "Приложение не назначает дефицит калорий и не ставит цели по темпу снижения веса. При подозрении на расстройства питания обратитесь к специалисту.",
        "days_spec": [],
    },
    {
        "id": "T19", "name": "Общая форма",
        "summary": "Две-три тренировки на всё тело плюс кондиция: поддержание здоровья без гонки за весами.",
        "principle": "рекомендации ВОЗ 2020 и ACSM 2026 по силовой и аэробной активности",
        "goals": ["general", "return", "weight_loss"], "levels": ["beginner", "intermediate"], "days": [2, 3, 4, 5, 6],
        "inventory": ["gym", "home_barbell", "dumbbells", "bodyweight", "kettlebell"], "session": [45, 60],
        "progression": "double", "engine_ready": True, "fallback": None,
        "cardio": {"zone2": "1–2 раза по 20–30 минут", "intervals": "1–2 интервальные по 15–25 минут"},
        "days_spec": [
            D("A", S(SQ, "main", (2, 3), (8, 15), ["goblet_squat", "back_squat_high_bar", "leg_press_45", "bodyweight_squat"], (2, 4)),
              S(HPU, "main", (2, 3), (8, 15), ["dumbbell_bench_press", "machine_chest_press", "dumbbell_floor_press", "push_up"], (2, 4)),
              S(HPL, "main", (2, 3), (8, 15), ["one_arm_dumbbell_row", "seated_cable_row", "kettlebell_row", "door_towel_row"], (2, 4)),
              S(CAE, "accessory", 2, (20, 40), CORE_AE, prog="time"), S(CR, "accessory", 2, (30, 60), ["farmers_walk", "suitcase_carry"], prog="time")),
            D("B", S(HG, "main", (2, 3), (8, 15), ["romanian_deadlift_db", "kb_deadlift", "back_extension_45", "rdl_bw"], (2, 4)),
              S(VPU, "main", (2, 3), (8, 15), ["dumbbell_shoulder_press_seated", "machine_shoulder_press", "kettlebell_press", "pike_push_up"], (2, 4)),
              S(VPL, "main", (2, 3), (8, 15), ["lat_pulldown_wide", "pull_up", "band_lat_pulldown", "door_towel_row"], (2, 4)),
              S(LU, "secondary", (2, 3), (8, 15), ["split_squat", "reverse_lunge", "step_up"], (2, 4)), S(CAR, "accessory", 2, (8, 12), ["pallof_press", "side_plank", "bird_dog"])),
        ],
    },
    {
        "id": "T20", "name": "50+: функциональная сила",
        "summary": "Мягкая силовая работа на тренажёрах и гантелях плюс упражнения на равновесие.",
        "principle": "рекомендации NSCA 2019, ВОЗ 2020 и ICFSR 2021 для старшего возраста",
        "goals": ["general", "return", "strength", "mass", "strength_mass", "weight_loss"],
        "levels": ["beginner", "intermediate"], "days": [2, 3], "inventory": ["gym", "dumbbells", "home_barbell", "bodyweight"],
        "session": [45, 60], "progression": "double", "engine_ready": True, "fallback": None,
        "warning": "65+ с падениями, головокружениями, неконтролируемым давлением или остеопоротическими переломами: только после допуска врача.",
        "phases": [
            {"weeks": "1–8", "scheme": "6–8 упражнений, 1–2 × 10–15, запас 3 и больше"},
            {"weeks": "9+", "scheme": "2–3 × 6–12 до 70–80% разового максимума, запас 1–3"},
            {"weeks": "со 2–3-го месяца", "scheme": "1–2 мощностных упражнения, 3–6 повторений, 40–60%, без отказа"},
        ],
        "days_spec": [
            D("Фулбоди", S(SQ, "main", (1, 2), (10, 15), ["leg_press_45", "goblet_squat", "sit_to_stand", "bodyweight_squat"], (3, 4)),
              S(HPU, "main", (1, 2), (10, 15), ["machine_chest_press", "dumbbell_floor_press", "incline_push_up", "wall_push_up"], (3, 4)),
              S(VPL, "main", (1, 2), (10, 15), ["lat_pulldown_wide", "band_lat_pulldown", "door_towel_row", "table_row"], (3, 4)),
              S(HPL, "main", (1, 2), (10, 15), ["seated_cable_row", "chest_supported_dumbbell_row", "door_towel_row", "table_row"], (3, 4)),
              S(HE, "secondary", (1, 2), (10, 15), ["hip_thrust_machine", "glute_bridge_bw"], (3, 4)),
              S(LU, "secondary", (1, 2), (10, 15), ["step_up", "split_squat"], (3, 4)),
              S(CAR, "accessory", 2, (8, 12), ["pallof_press", "side_plank", "bird_dog"])),
        ],
    },
    {
        "id": "T21", "name": "Тяжёлые лесенки (облегчённый)",
        "summary": "Три тяжёлых дня: жим, присед и тяга, подходы лесенкой по процентам. Для опытных.",
        "principle": "по принципам Шейко, облегчённый вариант: вывод из принципов, а не авторская программа",
        "goals": ["strength"], "levels": ["advanced"], "days": [3], "inventory": ["gym", "home_barbell"],
        "session": [60, 75], "progression": "block", "engine_ready": False, "fallback": "T07",
        "days_spec": [
            D("День 1", S(HPU, "main", 5, (3, 5), BENCH_MAIN, (1, 2), prog="block", ladder_sets=True), S(SQ, "main", 4, (3, 5), SQUAT_MAIN, (1, 2), prog="block"),
              S(HPU, "secondary", 3, (3, 5), ["close_grip_bench_press", "dumbbell_bench_press", "push_up"], (2, 3), prog="block")),
            D("День 2", S(HG, "main", 4, (3, 5), HINGE_MAIN, (1, 2), prog="block"), S(HPU, "main", 5, (3, 5), BENCH_MAIN, (1, 2), prog="block")),
            D("День 3", S(SQ, "main", 5, (3, 5), SQUAT_MAIN, (1, 2), prog="block"), S(HPU, "main", 5, (3, 5), BENCH_MAIN, (1, 2), prog="block")),
        ],
    },
    {
        "id": "T22", "name": "Пик силы: 6 недель",
        "summary": "Шесть недель подготовки к проверке максимумов: объём падает, нагрузка растёт.",
        "principle": "шестинедельный силовой пик (структура в духе Candito, проценты по зонам раздела 4.2)",
        "goals": ["strength"], "levels": ["intermediate"], "days": [3, 4, 5], "inventory": ["gym", "home_barbell"],
        "session": [60, 75], "progression": "block", "engine_ready": False, "fallback": "T07",
        "week_scheme": [["1–2", "подготовка и объём, около 80%, 5 дней"], ["3–4", "сила 85–90%, 4 дня"], ["5", "тест и пик, 3 дня"], ["6", "разгрузка, рестарт или проверка максимумов"]],
        "days_spec": [
            D("Верх", S(HPU, "main", (3, 5), (3, 5), BENCH_MAIN, (1, 2), prog="block"), S(HPL, "main", 4, (5, 8), ["barbell_bent_over_row", "seated_cable_row", "one_arm_dumbbell_row"], (1, 2)),
              S(VPU, "secondary", 3, (6, 8), OHP, (1, 2))),
            D("Низ", S(SQ, "main", (3, 5), (3, 5), SQUAT_MAIN, (1, 2), prog="block"), S(HG, "main", 3, (3, 5), HINGE_MAIN, (1, 2), prog="block"),
              S(KF, "accessory", 3, (8, 12), LEG_CURL)),
        ],
    },
]

# Лестницы прогрессий (data/progression_ladders_and_ru_names.md, 3.12): порядок = от лёгкого к сложному.
LADDERS: dict[str, dict[str, Any]] = {
    "L_PUSH_H": {"name": "Горизонтальный жим", "steps": ["wall_push_up", "incline_push_up", "knee_push_up", "push_up", "diamond_push_up", "archer_push_up", "pushup_pseudo_planche", "one_arm_push_up"], "advance": "3×8 чисто или 3×12–15"},
    "L_DIP": {"name": "Брусья", "steps": ["dip_support_hold", "dip_negative", "chest_dip", "weighted_dip"], "advance": "3×30 с, 3×5, 3×8"},
    "L_PUSH_V": {"name": "Вертикальный жим", "steps": ["pike_push_up", "elevated_pike_push_up", "handstand_wall_hold", "handstand_push_up"], "advance": "3×8"},
    "L_PULL_V": {"name": "Подтягивания", "steps": ["dead_hang", "scapular_pull_up", "arch_hang", "negative_pull_up", "band_assisted_pull_up", "chin_up", "pull_up", "weighted_pull_up"], "advance": "3×5, затем 3×8"},
    "L_PULL_H": {"name": "Горизонтальная тяга", "steps": ["door_towel_row", "ring_row", "inverted_row", "feet_elevated_inverted_row", "row_archer"], "advance": "3×8"},
    "L_SQUAT": {"name": "Присед", "steps": ["squat_assisted", "bodyweight_squat", "split_squat", "bulgarian_split_squat", "skater_squat"], "advance": "3×8–15"},
    "L_SQUAT_PISTOL": {"name": "Ветка к пистолету", "steps": ["bodyweight_squat", "step_up", "bulgarian_split_squat", "pistol_box", "pistol_squat"], "advance": "3×8"},
    "L_HINGE": {"name": "Наклон", "steps": ["rdl_bw", "single_leg_rdl", "nordic_band", "nordic_curl"], "advance": "3×8; нордические 2–3×3–5"},
    "L_GLUTE": {"name": "Ягодичные", "steps": ["glute_bridge_bw", "glute_bridge_sl", "single_leg_hip_thrust"], "advance": "3×12–15"},
    "L_ANTI_EXT": {"name": "Антиразгибание", "steps": ["dead_bug", "plank", "ab_wheel_rollout", "rollout_standing"], "advance": "удержание 3×30 с, динамика 3×8–12"},
    "L_HOLLOW": {"name": "«Лодочка»", "steps": ["dead_bug", "hollow_body_hold"], "advance": "3×30 с"},
    "L_ANTI_ROT": {"name": "Антиротация", "steps": ["bird_dog", "pallof_press", "side_plank", "copenhagen_plank"], "advance": "3×8–12 или 3×30 с"},
    "L_EXT": {"name": "Разгибание", "steps": ["arch_hold", "reverse_hyperextension"], "advance": "3×8–12 или 3×30 с"},
    "L_HANGING_CORE": {"name": "Вис", "steps": ["lying_leg_raise", "hanging_knee_raise", "hanging_leg_raise"], "advance": "3×8–12"},
    "L_LSIT": {"name": "Уголок", "steps": ["dip_support_hold", "lsit_tuck", "lsit"], "advance": "3×30 с"},
    "L_PLYO": {"name": "Плиометрика", "steps": ["plyo_snap_down", "plyo_pogo", "plyo_squat_jump", "plyo_broad_jump", "plyo_box_jump", "plyo_skater", "plyo_depth_jump"], "advance": "тихое приземление, без потери высоты более 10%"},
    "L_KB_HINGE": {"name": "Гиря: наклон", "steps": ["kb_deadlift", "kettlebell_swing", "kb_swing_1h", "kb_clean", "kb_snatch"], "advance": "техника и норматив по времени"},
    "L_KB_GETUP": {"name": "Турецкий подъём", "steps": ["kb_tgu"], "advance": "5×1 на сторону чисто"},
    "L_KB_PRESS": {"name": "Гиря: жим", "steps": ["kb_clean", "kettlebell_press", "kb_push_press"], "advance": "лесенка выполнена"},
}
