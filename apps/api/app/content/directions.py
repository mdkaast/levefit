"""Направления тренировок, акценты и заготовки сессий для не-силовых видов.

Структура готова к расширению, а содержимое бега, йоги, кроссфита и функционального тренинга пока
заготовка: исследования по этим видам (E6) нет, поэтому все сессии `verified=False`, без научных
обоснований и без прогрессии по неделям. Владелец может дозаказать исследование, не меняя код.
"""

from typing import Any

MAX_TRAINING_DAYS = 5  # макет Directions: «Занятий в неделю: N из 5 дней»
MAX_DAYS_PER_DIRECTION = 5
# Недельный объём группы мышц, выше которого акцент ничего не добавляет:
# в данных (programming_rules 4.1) отдача быстро падает около 20 подходов в неделю.
WEEKLY_SETS_CAP = 20
ACCENT_EXTRA_SETS = 2  # подходов в неделю на группу сверх базы (E4)
MAX_ACCENT_MUSCLES = 2

# Группы силуэта (8 из макетов) → группы интерфейса каталога (`muscles.ui_group`)
ACCENT_MUSCLES: dict[str, dict[str, Any]] = {
    "chest": {"name": "Грудные", "ui": ["chest"]},
    "biceps": {"name": "Бицепсы", "ui": ["biceps"]},
    "triceps": {"name": "Трицепсы", "ui": ["triceps"]},
    "delts": {"name": "Дельтовидные", "ui": ["front_delts", "side_delts", "rear_delts"]},
    "abs": {"name": "Пресс", "ui": ["abs"]},
    "lats": {"name": "Широчайшие", "ui": ["back_width"]},
    "glutes": {"name": "Ягодичные", "ui": ["glutes"]},
    "quads": {"name": "Квадрицепсы", "ui": ["quads"]},
}

# Прежние шесть групп профиля → новые восемь (для тех, кто выбрал акцент до фазы 3)
LEGACY_MUSCLES = {
    "chest": ["chest"],
    "back": ["lats"],
    "shoulders": ["delts"],
    "arms": ["biceps", "triceps"],
    "legs": ["quads"],
    "core": ["abs"],
}

# Кандидаты добавочного упражнения для акцента, от зала к дому и своему весу
ACCENT_ACCESSORY: dict[str, dict[str, Any]] = {
    "chest": {
        "pattern": "chest_isolation",
        "reps": [10, 15],
        "candidates": [
            "mid_cable_fly",
            "dumbbell_fly",
            "band_fly",
            "incline_dumbbell_press",
            "push_up",
        ],
    },
    "biceps": {
        "pattern": "elbow_flexion",
        "reps": [10, 15],
        "candidates": [
            "cable_curl",
            "dumbbell_curl",
            "barbell_curl",
            "band_curl",
            "bodyweight_curl",
        ],
    },
    "triceps": {
        "pattern": "elbow_extension",
        "reps": [10, 15],
        "candidates": [
            "rope_pushdown",
            "overhead_cable_extension",
            "seated_db_overhead_extension",
            "band_pushdown",
            "bodyweight_triceps_extension",
        ],
    },
    "delts": {
        "pattern": "shoulder_isolation",
        "reps": [12, 20],
        "candidates": [
            "cable_lateral_raise",
            "dumbbell_lateral_raise",
            "band_lateral_raise",
            "pike_push_up",
        ],
    },
    "abs": {
        "pattern": "core_flexion",
        "reps": [10, 20],
        "candidates": ["cable_crunch", "machine_crunch", "reverse_crunch", "crunch"],
    },
    "lats": {
        "pattern": "vertical_pull",
        "reps": [8, 12],
        "candidates": [
            "lat_pulldown_wide",
            "single_arm_lat_pulldown",
            "band_lat_pulldown",
            "dumbbell_pullover",
            "one_arm_dumbbell_row",
        ],
    },
    "glutes": {
        "pattern": "hip_extension",
        "reps": [8, 15],
        "candidates": ["hip_thrust_machine", "hip_thrust_bb", "hip_thrust_db", "glute_bridge_bw"],
    },
    "quads": {
        "pattern": "knee_extension",
        "reps": [10, 15],
        "candidates": ["leg_extension", "leg_press_45", "goblet_squat", "bodyweight_squat"],
    },
}

# Качества силового троеборья: какой паттерн получает лишний подход на главном движении
POWERLIFTING_PATTERN = {"squat": "squat", "bench": "horizontal_push", "deadlift": "hinge"}

DIRECTIONS: dict[str, dict[str, Any]] = {
    "gym": {"name": "Зал", "kind": "strength", "accent": "muscles", "default_days": 3},
    "powerlifting": {
        "name": "Пауэрлифтинг",
        "kind": "strength",
        "accent": "qualities",
        "default_days": 3,
    },
    "crossfit": {"name": "Кроссфит", "kind": "sessions", "accent": "qualities", "default_days": 2},
    "functional": {
        "name": "Функциональный",
        "kind": "sessions",
        "accent": "qualities",
        "default_days": 2,
    },
    "running": {"name": "Бег", "kind": "sessions", "accent": "qualities", "default_days": 2},
    "yoga": {"name": "Йога", "kind": "sessions", "accent": "qualities", "default_days": 2},
    "home": {"name": "Дом", "kind": "strength", "accent": "muscles", "default_days": 3},
    "universal": {"name": "Универсальный", "kind": "auto", "accent": None, "default_days": 3},
}

QUALITIES: dict[str, dict[str, str]] = {
    "powerlifting": {
        "squat": "Присед",
        "bench": "Жим",
        "deadlift": "Тяга",
        "technique": "Техника",
        "peak": "Пиковая сила",
        "accessories": "Подсобка",
    },
    "crossfit": {
        "strength": "Сила",
        "gymnastics": "Гимнастика",
        "metcon": "Метаболическая выносливость",
        "olympic": "Олимпийские",
        "mobility": "Мобильность",
    },
    "functional": {
        "core": "Сила корпуса",
        "power": "Мощность",
        "mobility": "Подвижность",
        "balance": "Баланс",
        "conditioning": "Кондиция",
    },
    "running": {
        "aerobic": "Аэробная база",
        "threshold": "Темп и порог",
        "speed": "Скорость",
        "long": "Выносливость к длинным",
        "recovery": "Восстановление",
    },
    "yoga": {
        "flexibility": "Гибкость",
        "strength_balance": "Сила и баланс",
        "recovery": "Восстановление",
        "posture": "Спина и осанка",
        "relaxation": "Расслабление",
    },
}

DEFAULT_QUALITY = {
    "powerlifting": "squat",
    "crossfit": "metcon",
    "functional": "core",
    "running": "aerobic",
    "yoga": "flexibility",
}


def _s(key, name, quality, minutes, hard, blocks, tags=()):
    return {
        "key": key,
        "name": name,
        "quality": quality,
        "minutes": minutes,
        "hard": hard,
        "tags": list(tags),
        "blocks": list(blocks),
        "verified": False,
    }


# Заготовки сессий: 6 на направление. Структура описана общими словами; точные дозировки не заданы.
SESSION_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "running": [
        _s(
            "run_easy",
            "Лёгкий бег",
            "aerobic",
            30,
            False,
            ["Разминка 5 мин ходьбой", "Бег в разговорном темпе", "Заминка 5 мин"],
        ),
        _s(
            "run_long",
            "Длинный бег",
            "long",
            50,
            False,
            ["Бег в лёгком темпе дольше обычного", "Вода и остановки по самочувствию"],
        ),
        _s(
            "run_tempo",
            "Темповый бег",
            "threshold",
            35,
            True,
            ["Разминка", "Непрерывный отрезок в напряжённом, но ровном темпе", "Заминка"],
            ("intervals",),
        ),
        _s(
            "run_intervals",
            "Интервалы",
            "speed",
            35,
            True,
            ["Разминка", "Быстрые отрезки с лёгким бегом между ними", "Заминка"],
            ("intervals",),
        ),
        _s(
            "run_fartlek",
            "Фартлек",
            "speed",
            35,
            True,
            ["Бег с произвольными ускорениями по ощущениям"],
            ("intervals",),
        ),
        _s(
            "run_recovery",
            "Восстановительный бег",
            "recovery",
            25,
            False,
            ["Очень лёгкий темп, дыхание свободное"],
        ),
    ],
    "yoga": [
        _s(
            "yoga_flex",
            "Гибкость",
            "flexibility",
            30,
            False,
            ["Мягкая разминка суставов", "Удержания растяжек без боли", "Расслабление в конце"],
        ),
        _s(
            "yoga_strength",
            "Сила и баланс",
            "strength_balance",
            40,
            False,
            ["Стойки и баланс на одной ноге", "Удержания поз на силу корпуса"],
        ),
        _s(
            "yoga_recovery",
            "Восстановление",
            "recovery",
            25,
            False,
            ["Спокойный темп, дыхание, мягкие скручивания"],
        ),
        _s(
            "yoga_posture",
            "Спина и осанка",
            "posture",
            30,
            False,
            ["Подвижность грудного отдела", "Упражнения на лопатки и корпус"],
        ),
        _s(
            "yoga_relax",
            "Расслабление",
            "relaxation",
            20,
            False,
            ["Дыхание", "Положения лёжа с удержанием", "Завершающее расслабление"],
        ),
        _s(
            "yoga_morning",
            "Утренняя",
            "flexibility",
            15,
            False,
            ["Короткий комплекс для разминки после сна"],
        ),
    ],
    "crossfit": [
        _s(
            "cf_amrap",
            "AMRAP",
            "metcon",
            30,
            True,
            ["Разминка", "Круг упражнений на максимум кругов за заданное время"],
            ("intervals",),
        ),
        _s(
            "cf_emom",
            "EMOM",
            "metcon",
            30,
            True,
            ["Разминка", "Каждую минуту одно задание, остаток минуты на отдых"],
            ("intervals",),
        ),
        _s(
            "cf_fortime",
            "For time",
            "metcon",
            30,
            True,
            ["Разминка", "Заданный объём на скорость"],
            ("intervals",),
        ),
        _s(
            "cf_strength",
            "Сила и короткий меткон",
            "strength",
            50,
            True,
            ["Базовое движение в подходах", "Короткий метаболический круг"],
            ("heavy_legs",),
        ),
        _s(
            "cf_gym",
            "Гимнастика",
            "gymnastics",
            40,
            False,
            ["Работа на турнике, в упорах и стойках", "Техника, без работы до отказа"],
        ),
        _s(
            "cf_mobility",
            "Мобильность и техника",
            "mobility",
            30,
            False,
            ["Подвижность таза и плеч", "Техника движений с лёгким весом"],
        ),
    ],
    "functional": [
        _s(
            "fn_core",
            "Корпус",
            "core",
            30,
            False,
            ["Антиэкстензия и антиротация", "Переносы груза"],
        ),
        _s(
            "fn_power",
            "Мощность",
            "power",
            35,
            True,
            ["Прыжки и броски небольшим весом", "Отдых между подходами полный"],
            ("heavy_legs",),
        ),
        _s(
            "fn_mobility",
            "Подвижность",
            "mobility",
            30,
            False,
            ["Суставная гимнастика", "Удержания в глубоких положениях без боли"],
        ),
        _s(
            "fn_balance",
            "Баланс",
            "balance",
            30,
            False,
            ["Работа на одной ноге", "Нестабильные опоры без веса"],
        ),
        _s(
            "fn_cond",
            "Кондиция",
            "conditioning",
            35,
            True,
            ["Круг из базовых движений с собственным весом"],
            ("intervals",),
        ),
        _s(
            "fn_circuit",
            "Круговая тренировка",
            "conditioning",
            40,
            False,
            ["Станции по 40 секунд, переход 20 секунд"],
        ),
    ],
}


def direction_keys() -> list[str]:
    return list(DIRECTIONS)


def accent_options(direction: str) -> list[dict[str, str]]:
    """Чипы для выбора акцента: группы мышц для силовых направлений или качества."""
    info = DIRECTIONS[direction]
    if info["accent"] == "muscles":
        return [{"key": k, "name": v["name"]} for k, v in ACCENT_MUSCLES.items()]
    if info["accent"] == "qualities":
        return [{"key": k, "name": n} for k, n in QUALITIES[direction].items()]
    return []


def valid_accent(direction: str, selection: list[str]) -> bool:
    keys = {o["key"] for o in accent_options(direction)}
    unique = len(set(selection)) == len(selection)
    return bool(keys) and unique and len(selection) <= MAX_ACCENT_MUSCLES and set(selection) <= keys
