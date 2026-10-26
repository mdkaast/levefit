"""Параметры движка решений. Источник правил: data/programming_rules.md (раздел 4).

Метки доказательности: [С] мета-анализы, [К] консенсус экспертов, [П] практика тренеров
(шаги, пороги и проценты — не результат контролируемых сравнений). Любое изменение числа
здесь требует повышения RULES_VERSION: версия пишется в журнал решений (M7).
"""

RULES_VERSION = "1.0"

# --- Двойная прогрессия [К/П] ---
DOUBLE_PROGRESSION_SPAN = 2  # диапазон повторений: [верх − 2 … верх]
DEFAULT_TOP_REPS = {
    "strength": 5,
    "strength_mass": 6,
    "mass": 10,
    "return": 10,
    "weight_loss": 12,
    "general": 12,
    "shape": 10,
}
DEFAULT_TOP_REPS_FALLBACK = 10
BODYWEIGHT_TOP_CAP = 30

# --- Шаг веса [К/П]: 2,5 кг; низ тела у новичка +5 кг; рамка 2–10% за шаг ---
DEFAULT_STEP_KG = 2.5
LOWER_BODY_BEGINNER_STEP_KG = 5.0
LOWER_BODY_GROUPS = ("legs",)
MAX_GAIN_PCT = 0.10  # рост веса за сессию не больше max(10%, шаг) (4.10)

# --- Целевой RIR и коррекция по нему [П] ---
TARGET_RIR = 2
BEGINNER_MIN_TARGET_RIR = 2  # новичку RIR < 2 в базовых запрещён (4.10)
RIR_ADJUST_PCT = 0.04  # ±4% веса за каждое повторение расхождения
RIR_GAP_TRIGGER = 2  # реагируем при расхождении на 2 и более
RIR_MAX_UP_STEPS = 2

# --- Застой и сброс [П] ---
RESET_PCT = 0.075  # −5…10% при втором провале подряд на том же весе
SAME_WEIGHT_TOLERANCE_KG = 0.01

# --- Боль [П]: общая модификация, не лечение ---
PAIN_REDUCE_PCT = 0.20  # 6.3: снизить вес на 20–50%, берём нижнюю границу

# --- Разгрузка [К/П] ---
DELOAD_SETS_FACTOR = 0.55  # подходы −40…50%
DELOAD_RIR_PLUS = 2
DELOAD_SIGNALS_REQUIRED = 2  # ≥2 из 4 сигналов за 7–10 дней
DELOAD_E1RM_DROP = 0.05
DELOAD_LOW_READINESS_COUNT = 2
DELOAD_SKIPS_COUNT = 2  # пропусков за окно
SKIPS_WINDOW_DAYS = 10
SCHEDULED_DELOAD_WEEKS = {"beginner": 8, "intermediate": 5, "advanced": 5}
SCHEDULED_DELOAD_DEFAULT_WEEKS = 6
SCHEDULED_DELOAD_MIN_SESSIONS = 6

# --- Возврат после перерыва [П]; в спорных местах взята консервативная граница ---
# (до скольки дней включительно, снижение веса, множитель объёма)
RETURN_TABLE = (
    (7, 0.0, 1.0),
    (14, 0.10, 0.75),
    (28, 0.20, 0.70),
    (60, 0.30, 0.50),
    (180, 0.40, 0.50),
    (10_000, 0.40, 0.50),
)
RETURN_RECALIBRATE_AFTER_DAYS = 180  # дольше — как новичок, нужна тестовая сессия
RETURN_AGE_SHIFT_FROM = 40  # старше: строка таблицы сдвигается на одну вниз

# --- Готовность перед тренировкой [С/П]: «лёгкий день» ---
LIGHT_DAY_LOW = 2  # сон или энергия не выше
LIGHT_DAY_WEIGHT_PCT = 0.10
LIGHT_DAY_SETS_MINUS = 1
LIGHT_DAY_RIR_PLUS = 1
