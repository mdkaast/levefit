"""Конвертер каталога: data/exercises.json (374 записи с русскими сокращениями) → структурированный JSON.

Запуск из корня репозитория:  python -X utf8 scripts/build_catalog.py

Результат кладётся внутрь API (apps/api/app/content/), потому что образ API собирается только из
этой папки. Вместе с каталогом пишется import_report.json: что не удалось сопоставить, дубли,
ссылки на несуществующие упражнения. Поля, выведенные разбором, помечены `parsed`; запись
`verified: false`, если в данных есть оговорка «неустоявшееся название» или упражнение в списке
на вычитку (data/progression_ladders_and_ru_names.md, раздел 3.13).
"""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "exercises.json"
OUT = ROOT / "apps" / "api" / "app" / "content"

# ---------- паттерны движения (data_schema.md, 2.3) ----------
PATTERNS = {
    "SQ": "squat", "HG": "hinge", "LU": "lunge", "HE": "hip_extension", "KE": "knee_extension",
    "KF": "knee_flexion", "CA": "calf_raise", "AD": "hip_adduction", "AB": "hip_abduction",
    "HPU": "horizontal_push", "VPU": "vertical_push", "CHI": "chest_isolation",
    "SHI": "shoulder_isolation", "EE": "elbow_extension", "VPL": "vertical_pull",
    "HPL": "horizontal_pull", "SC": "scapular", "RD": "rear_delt", "EF": "elbow_flexion",
    "GR": "grip_forearm", "C-AE": "core_anti_extension", "C-AR": "core_anti_rotation",
    "C-FL": "core_flexion", "C-RO": "core_rotation", "C-EX": "core_extension", "CR": "carry",
    "KB": "kb_skill", "PLY": "plyometric", "COND": "conditioning", "WU": "warmup", "MOB": "mobility",
}
PATTERN_RE = re.compile(r"(?<![A-Z-])(C-(?:AE|AR|FL|RO|EX)|" + "|".join(k for k in PATTERNS if not k.startswith("C-")) + r")(?![A-Za-z-])")

# ---------- инвентарь ----------
EQUIP = {
    "ШТ": "barbell", "EZ": "ez_bar", "ГАН": "dumbbell", "ГИР": "kettlebell", "БЛ": "cable",
    "ТР": "machine_stack", "РЫЧ": "plate_machine", "СМ": "smith", "СТ": "rack", "СК": "bench",
    "ЛМ": "landmine", "ТРЭП": "trap_bar", "ТУР": "pullup_bar", "перекладина": "pullup_bar",
    "БР": "dip_bars", "ПЕТ": "rings", "РЕЗ": "band", "ГРАВ": "assist_machine", "СВ": "bodyweight",
    "GHD": "ghd", "Смит": "smith", "кольца": "rings", "эспандер": "band", "РЕЗ-петля": "band",
    "тренажёр": "machine_stack", "скамья": "bench", "блин": "plates", "блины": "plates",
    "скакалка": "jump_rope", "сани": "sled", "гребной": "cardio_machine", "эйрбайк": "cardio_machine",
    "вело": "cardio_machine", "дорожка": "cardio_machine", "степпер": "cardio_machine",
    "кардиотренажёр": "cardio_machine",
}
# бытовые предметы: считаются доступными всегда, в требования не входят
HOUSEHOLD = {
    "опора", "стена", "ящик", "стул", "стулья", "стула", "стол", "диван", "платформа", "канат", "пол",
    "пояс", "палка", "фитбол", "ролик", "роллер", "полотенце", "полотенца", "тумба", "ступенька",
    "рукояти", "V-рукоять", "D-рукоять", "V", "D", "рама", "блок", "гриф", "стойка", "слайдер",
    "накладка", "манжета", "фиксация", "ног", "кг", "параллетсы", "низкая", "опц.", "спец.",
    "СК-гипер", "накл.", "любой", "улица", "лестница", "мяч", "подушка", "партнёр", "дверной",
    "проём", "дверь", "крепление", "жилет", "груз", "лямки", "ремень", "упоры", "утяжелители",
    "медбол", "снаряд", "рабочий", "устойчивый", "верхнее", "высокая", "со", "спинкой", "Скотта",
    "уровни", "1–5", "2", "5–10",
}

LEVELS = {"Н": "beginner", "С": "intermediate", "П": "advanced"}

# ---------- флаги нагрузки (data_schema.md, 2.6) ----------
FLAGS = {
    "ОСЕВ": "axial_spinal_load", "П-СГ": "lumbar_flexion_load", "П-РЗ": "lumbar_extension_load",
    "ГЛУБ": "deep_knee_flexion", "КОЛ": "knee_pain", "ПФ": "patellofemoral_sensitive",
    "ТБС": "hip_impingement_deep_flexion", "ГОЛЕН": "ankle_mobility_required",
    "БАЛ": "balance_demand", "ХВАТ": "grip_limited", "ВАЛ": "hernia_valsalva",
    "БЕР": "pregnancy_supine_caution", "DOMS": "high_eccentric_doms", "ИМП": "impingement_position",
    "ПЛ-КР": "shoulder_end_range", "ШЕЯ": "neck_strain", "ПАД": "fall_risk",
    "ОПОРА": "door_equipment", "РЕЗ!": "band_snap", "ЧИТ": "swing_cheat", "УДАР": "high_impact",
    "ПЕРЕВ": "inverted",
}
FLAG_RE = re.compile(
    r"^(ОСЕВ|П-СГ|П-РЗ|ГЛУБ|КОЛ|ПФ|ТБС|ГОЛЕН|БАЛ|ХВАТ|ВАЛ|БЕР|DOMS|ИМП|ПЛ-КР|ШЕЯ|ПАД|ОПОРА|РЕЗ!|ЧИТ|УДАР|ПЕРЕВ"
    r"|ПЛ|ЛОК|ЗАП)(\d)?(?:[–-](\d))?"
)
JOINT = {"ПЛ": "shoulder", "ЛОК": "elbow", "ЗАП": "wrist"}

SCENARIOS = {"бШ": "noBB", "Д": "DB", "СВ": "BW", "К": "KNEE", "П": "LB", "Пл": "SH", "Л": "EL"}
SCENARIO_RE = re.compile(r"(?:^|[;·]\s*)(бШ|Пл|Д|СВ|К|П|Л):\s*")

# ---------- мышцы ----------
# (регулярное выражение, id мышцы, UI-группа). Порядок важен: частные раньше общих.
MUSCLES = [
    (r"ягод-ср|средн\w* ягод|ягод\.?\s*ср|ср\.?\s*ягод", "glute_med_min", "glutes"),
    (r"ягод", "glute_max", "glutes"),
    (r"квадр|\bноги\b", "quadriceps", "quads"),
    (r"привод", "adductors", "adductors"),
    (r"з\.\s*бедро|бедро|бицепс бедра|сгибатели бедра(?! )", "hamstrings", "hamstrings"),
    (r"разг\.\s*сп|разгибатели спины|поясниц(?!ы\b)", "erector_spinae", "lower_back"),
    (r"широч", "lats", "back_width"),
    (r"круглая большая", "teres_major", "back_width"),
    (r"ромб", "rhomboids", "back_thickness"),
    (r"трап", "traps", "traps"),
    (r"з\.\s*дельта|задн\w* дельт|задняя дельта", "rear_delt", "rear_delts"),
    (r"ср\.\s*дельта|средн\w* дельт|ср\.?\s*дельт", "side_delt", "side_delts"),
    (r"п\.\s*дельта|передн\w* дельт|\(п\)|дельт|плечи|плеч\b", "front_delt", "front_delts"),
    (r"грудь|груд", "pectorals", "chest"),
    (r"трицепс", "triceps", "triceps"),
    (r"бицепс", "biceps", "biceps"),
    (r"плечелуч", "brachioradialis", "forearms"),
    (r"плечев", "brachialis", "biceps"),
    (r"предплечь|хват|запяст|сгибатели|разгибатели кисти", "forearms", "forearms"),
    (r"пресс|прямая мышца живота", "rectus_abdominis", "abs"),
    (r"косые", "obliques", "abs"),
    (r"поперечная", "transverse_abdominis", "abs"),
    (r"квадратная", "quadratus_lumborum", "lower_back"),
    (r"сгибатели бедра|подвздошно", "hip_flexors", "abs"),
    (r"кор\b|кора|корпус|антиротация", "core", "abs"),
    (r"икроножн", "gastrocnemius", "calves"),
    (r"камбаловид|икры", "soleus", "calves"),
    (r"большеберц", "tibialis_anterior", "calves"),
    (r"зубчат", "serratus", "serratus"),
    (r"ротатор|вращательная манжета", "rotator_cuff", "rear_delts"),
    (r"верх(?:ние)? спины|спина|спины", "upper_back", "back_thickness"),
]
MUSCLE_RE = [(re.compile(p, re.IGNORECASE), mid, grp) for p, mid, grp in MUSCLES]

# Старые 6 групп приложения (для совместимости с прежним кодом и онбордингом)
LEGACY_GROUP = {
    "chest": "chest", "back_width": "back", "back_thickness": "back", "traps": "back",
    "lower_back": "back", "front_delts": "shoulders", "side_delts": "shoulders",
    "rear_delts": "shoulders", "biceps": "arms", "triceps": "arms", "forearms": "arms",
    "quads": "legs", "hamstrings": "legs", "glutes": "legs", "adductors": "legs", "calves": "legs",
    "abs": "core", "serratus": "chest",
}
PATTERN_FALLBACK_GROUP = {
    "squat": "legs", "hinge": "legs", "lunge": "legs", "hip_extension": "legs", "knee_extension": "legs",
    "knee_flexion": "legs", "calf_raise": "legs", "hip_adduction": "legs", "hip_abduction": "legs",
    "horizontal_push": "chest", "vertical_push": "shoulders", "chest_isolation": "chest",
    "shoulder_isolation": "shoulders", "elbow_extension": "arms", "vertical_pull": "back",
    "horizontal_pull": "back", "scapular": "back", "rear_delt": "shoulders", "elbow_flexion": "arms",
    "grip_forearm": "arms", "core_anti_extension": "core", "core_anti_rotation": "core",
    "core_flexion": "core", "core_rotation": "core", "core_extension": "back", "carry": "full_body",
    "kb_skill": "full_body", "plyometric": "legs", "conditioning": "full_body", "warmup": "full_body",
    "mobility": "full_body",
}

# Названия, которые каталог сам помечает как неустоявшиеся (раздел 3.13): нужна вычитка тренером.
UNSETTLED = {
    "safety_bar_squat", "pendulum_squat", "heel_elevated_squat", "spanish_squat", "b_stance_rdl",
    "frog_pump", "reverse_nordic", "mcgill_curl_up", "tibialis_raise", "copenhagen_plank",
    "pallof_press", "squeeze_press", "landmine_press", "landmine_squat", "pike_push_up", "jm_press",
    "z_press", "svend_press", "pushup_pseudo_planche", "archer_push_up", "archer_pull_up",
    "feet_assisted_pull_up", "arch_hang", "seal_row", "kroc_row", "meadows_row", "iso_lateral_row",
    "table_row", "door_towel_row", "prone_ytw_raise", "scapular_retraction_cable", "band_pull_apart",
    "spider_curl", "bayesian_cable_curl", "drag_curl", "plate_pinch", "wrist_roller", "skater_squat",
    "wu_worlds_greatest", "mob_couch_stretch",
}


def num(text: str) -> float | None:
    m = re.search(r"\d+(?:[.,]\d+)?", text)
    return float(m.group(0).replace(",", ".")) if m else None


def parse_patterns(raw: str) -> tuple[str, list[str], bool]:
    codes: list[str] = []
    for m in PATTERN_RE.finditer(raw):
        name = PATTERNS[m.group(1)]
        if name not in codes:
            codes.append(name)
    unilateral = bool(re.search(r"1 нога|одна нога|попеременно", raw))
    return (codes[0] if codes else "other"), codes[1:], unilateral


def parse_equipment(raw: str, report: Counter) -> list[list[str]]:
    """«ГАН/ГИР/ШТ» → [[dumbbell],[kettlebell],[barbell]]; «ШТ+СТ» → [[barbell, rack]]."""
    if "спец. гриф" in raw:
        return [["special_bar", "rack"]]
    text = re.sub(r"\([^)]*\)", " ", raw).replace("накл.", " ").replace("СК-гипер", "СК")
    if text.strip() in ("", "—"):
        return [["bodyweight"]]
    alternatives: list[list[str]] = []
    for alt in re.split(r"\s*/\s*|,", text):
        items: list[str] = []
        for tok in re.split(r"\s*\+\s*", alt.strip()):
            for word in tok.split():
                if word in EQUIP:
                    if EQUIP[word] not in items:
                        items.append(EQUIP[word])
                elif word in HOUSEHOLD:
                    continue
                elif word:
                    report[f"equip:{word}"] += 1
        if items:
            alternatives.append(items)
    return alternatives or [["bodyweight"]]


def clean_slug(slug: str) -> str:
    """«table_row (hp20)» → «table_row»: старый номер в скобках не часть идентификатора."""
    return re.sub(r"\s*\(.*\)$", "", slug).strip()


REF_FIX = {"hip_thrust": "hip_thrust_bb", "pushdown": "cable_pushdown_bar"}
PATTERN_DEFAULT_MUSCLES = {
    "kb_skill": [("glute_max", "glutes"), ("hamstrings", "hamstrings"), ("core", "abs")],
    "plyometric": [("quadriceps", "quads"), ("glute_max", "glutes"), ("gastrocnemius", "calves")],
}


def parse_level(raw: str) -> str:
    m = re.match(r"\s*([НСП])", raw)
    return LEVELS[m.group(1)] if m else "intermediate"


def load_info(step: str, equipment: list[list[str]], pattern: str) -> tuple[str, float | None, float | None]:
    """(тип нагрузки, шаг, шаг для новичка) — по колонке «шаг» и инвентарю."""
    s = step.strip()
    beginner = None
    mb = re.search(r"Н:\s*(\d+(?:[.,]\d+)?)", s)
    if mb:
        beginner = float(mb.group(1).replace(",", "."))
    first = equipment[0][0] if equipment else "bodyweight"
    if "ГИР4" in s:
        return "kettlebell", 4.0, beginner
    if "СТЕК" in s:
        return ("cable" if first == "cable" else "machine_stack"), 5.0, beginner
    if "РЫЧ5" in s:
        return "plate_loaded", 5.0, beginner
    if "ДОБ" in s:
        return "bodyweight_added", 2.5, beginner
    if "РЕЗ" in s and not re.match(r"^\d", s):
        return "band_resistance", None, beginner
    if "ДИСТ" in s:
        return "carry_distance", None, beginner
    if re.match(r"^(ВР|время|с\b)", s) or pattern in ("core_anti_extension", "core_anti_rotation") and "ВР" in s:
        return "isometric_time", None, beginner
    if "контакты" in s:
        return "plyometric", None, beginner
    if s.startswith("ГАН"):
        return "dumbbell", 2.5, beginner
    if re.match(r"^[ПпВв]", s) and ("ПОВТ" in s or "повт" in s):
        return ("bodyweight_added" if "ДОБ" in s else "bodyweight"), None, beginner
    n = num(s)
    kind = {
        "barbell": "barbell", "ez_bar": "ez_bar", "dumbbell": "dumbbell", "kettlebell": "kettlebell",
        "cable": "cable", "machine_stack": "machine_stack", "plate_machine": "plate_loaded",
        "smith": "smith", "trap_bar": "barbell", "landmine": "barbell", "bodyweight": "bodyweight",
        "band": "band_resistance",
    }.get(first)
    if kind is None:
        kind = "bodyweight"
    if n is not None and kind not in ("bodyweight", "band_resistance"):
        return kind, n, beginner
    default = {"barbell": 2.5, "ez_bar": 2.5, "dumbbell": 2.5, "kettlebell": 4.0, "cable": 5.0,
               "machine_stack": 5.0, "plate_loaded": 5.0, "smith": 2.5}.get(kind)
    return kind, default, beginner


def e1rm_flag(raw: str) -> str:
    c = raw.strip()[:1]
    return {"Д": "yes", "Ч": "partial", "Н": "no"}.get(c, "no")


def parse_muscles(raw: str, report: Counter) -> list[dict]:
    """Первая часть до «;» — основные мышцы, после — вспомогательные и стабилизаторы."""
    text = raw.replace("(акцент)", "")
    parts = text.split(";")
    result: dict[str, dict] = {}
    for index, part in enumerate(parts):
        role = "primary" if index == 0 else "secondary"
        found = False
        remaining = part
        for rx, mid, grp in MUSCLE_RE:
            if rx.search(remaining):
                found = True
                if mid not in result:
                    result[mid] = {"muscle": mid, "role": role, "ui_group": grp}
                remaining = rx.sub(" ", remaining)
        if not found and part.strip():
            report[f"muscle:{part.strip()[:40]}"] += 1
    weights = {"primary": 1.0, "secondary": 0.5, "stabilizer": 0.25}
    out = []
    for item in result.values():
        item["volume_weight"] = weights[item["role"]]
        out.append(item)
    return out


def parse_notes(notes: str, ids: set[str], report: Counter) -> dict:
    aliases: list[str] = []
    variant_of = None
    for m in re.finditer(r"(?:^|[;·`]\s*)=\s*([a-z0-9_, ]+)", notes):
        aliases += [clean_slug(a) for a in m.group(1).split(",") if a.strip()]
    m = re.search(r"variant_of\s+([a-z0-9_]+)", notes)
    if m:
        variant_of = m.group(1)

    parts = [p.strip() for p in notes.split("·")]
    flag_text = parts[-1] if len(parts) > 1 else (notes if not SCENARIO_RE.search(notes) else "")
    # замены по сценариям: ищем во всех частях, где есть «Сценарий: …»
    subs: dict[str, list[str]] = {}
    for part in parts:
        pieces = SCENARIO_RE.split(part)
        # split возвращает [до, ключ, текст, ключ, текст, ...]
        for i in range(1, len(pieces) - 1, 2):
            key = SCENARIOS[pieces[i]]
            slugs = re.findall(r"[a-z][a-z0-9_]{2,}", pieces[i + 1].split(";")[0])
            subs.setdefault(key, [])
            for slug in slugs:
                if slug not in subs[key]:
                    subs[key].append(slug)
    flags: list[str] = []
    for token in re.split(r"[,;]", flag_text):
        t = token.strip()
        if not t or SCENARIO_RE.match(t) or t.startswith(("variant_of", "=", "как у")):
            continue
        m = FLAG_RE.match(t)
        if not m:
            continue
        base = m.group(1)
        if base in JOINT:
            level = m.group(3) or m.group(2)
            name = JOINT[base] + (f"_{level}" if level else "")
        else:
            name = FLAGS[base]
        if name not in flags:
            flags.append(name)
    for scenario in list(subs):
        fixed: list[str] = []
        for slug in subs[scenario]:
            slug = REF_FIX.get(slug, slug)
            if slug in ids:
                if slug not in fixed:
                    fixed.append(slug)
            else:
                report[f"missing_ref:{slug}"] += 1
        subs[scenario] = fixed
    return {"aliases": aliases, "variant_of": variant_of, "subs": subs, "flags": flags}


def main() -> None:
    source = json.loads(SRC.read_text(encoding="utf-8"))
    for x in source:
        x["id"] = clean_slug(x["id"])
    ids = {x["id"] for x in source}
    raw_by_id = {x["id"]: x for x in source}
    report: Counter = Counter()
    exercises = []
    for x in source:
        pattern, secondary, unilateral = parse_patterns(x["pattern"])
        equipment = parse_equipment(x["equipment"], report)
        load_type, step, step_beginner = load_info(x["step"], equipment, pattern)
        muscles = parse_muscles(x["muscles"], report)
        notes = parse_notes(x["notes_flags"], ids, report)
        muscles_source = "catalog"
        if not any(m["role"] == "primary" for m in muscles):
            base = raw_by_id.get(notes["variant_of"] or "")
            if base:  # «как high-bar»: те же мышцы, что у основного упражнения
                muscles = parse_muscles(base["muscles"], report)
                muscles_source = f"variant_of:{base['id']}"
            elif pattern in PATTERN_DEFAULT_MUSCLES:
                muscles = [
                    {"muscle": m, "role": "primary", "ui_group": g, "volume_weight": 1.0}
                    for m, g in PATTERN_DEFAULT_MUSCLES[pattern]
                ]
                muscles_source = "pattern_default"
        ui_groups = []
        for m in muscles:
            if m["role"] == "primary" and m["ui_group"] not in ui_groups:
                ui_groups.append(m["ui_group"])
        legacy = next((LEGACY_GROUP[g] for g in ui_groups if g in LEGACY_GROUP), None)
        if legacy is None:
            legacy = PATTERN_FALLBACK_GROUP.get(pattern, "full_body")
        category = {"conditioning": "cardio", "warmup": "mobility", "mobility": "mobility"}.get(
            pattern, "strength"
        )
        if "is_drill" in x["notes_flags"]:  # техническая отработка движения — не силовое упражнение
            category = "mobility"
        if not muscles:
            report["no_muscles"] += 1
        exercises.append(
            {
                "slug": x["id"],
                "name_ru": x["name_ru"],
                "name_en": x["name_en"],
                "pattern": pattern,
                "pattern_secondary": secondary,
                "unilateral": unilateral,
                "category": category,
                "legacy_group": legacy,
                "ui_groups": ui_groups,
                "level": parse_level(x["level"]),
                "equipment": equipment,
                "equipment_raw": x["equipment"],
                "load_type": load_type,
                "load_increment_kg": step,
                "load_increment_beginner_kg": step_beginner,
                "e1rm": e1rm_flag(x["e1rm"]),
                "muscles": muscles,
                "muscles_source": muscles_source,
                "caution_flags": notes["flags"],
                "subs": notes["subs"],
                "aliases": notes["aliases"],
                "variant_of": notes["variant_of"] if notes["variant_of"] in ids else None,
                "verified": x["id"] not in UNSETTLED and "неуст" not in x["notes_flags"],
                "source": "catalog",
                "section": x["group"],
            }
        )
    known = {e["slug"] for e in exercises}
    for e in exercises:
        for alias in e["aliases"]:
            if alias in known and alias != e["slug"]:
                report["alias_also_a_record"] += 1
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "exercises.json").write_text(
        json.dumps(exercises, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    summary = {
        "total": len(exercises),
        "by_pattern": dict(Counter(e["pattern"] for e in exercises).most_common()),
        "by_level": dict(Counter(e["level"] for e in exercises)),
        "by_load_type": dict(Counter(e["load_type"] for e in exercises)),
        "without_primary_muscles": [e["slug"] for e in exercises if not any(m["role"] == "primary" for m in e["muscles"])],
        "unverified": sorted(e["slug"] for e in exercises if not e["verified"]),
        "unparsed": {k: v for k, v in sorted(report.items())},
    }
    (OUT / "import_report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({k: v for k, v in summary.items() if k not in ("unverified",)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
