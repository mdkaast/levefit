"""Единый конфиг игровых констант. Стартовые значения, подлежат подтверждению владельцем."""

APPEARANCES = ("warrior", "runner", "sage")
GOALS = ("strength", "strength_mass", "mass", "return", "weight_loss", "general", "shape")
EQUIPMENT = ("gym", "home", "none")

DEFAULT_WORKOUTS_PER_WEEK = 3
MIN_WORKOUTS_PER_WEEK = 1
MAX_WORKOUTS_PER_WEEK = 7

CHARACTER_NAME_MAX_LEN = 30

# --- Профиль (онбординг) ---
GENDERS = ("male", "female", "other")
EXPERIENCE_LEVELS = ("beginner", "intermediate", "advanced")
# Образ жизни вне тренировок: сидячий, лёгкий, активный, тяжёлый физический труд.
LIFESTYLES = ("sedentary", "light", "active", "very_active")
TARGET_MUSCLES = ("chest", "back", "shoulders", "arms", "legs", "core")
MIN_AGE, MAX_AGE = 12, 100
MIN_HEIGHT_CM, MAX_HEIGHT_CM = 120, 230

EXERCISE_CATEGORIES = ("strength", "cardio", "mobility")
WORKOUT_STATUSES = ("planned", "in_progress", "finished")

# --- XP (стартовые значения, подтверждены владельцем) ---
XP_WORKOUT = 50
XP_PER_SET = 5
XP_WEIGHT_ENTRY = 5
XP_DAILY_TASK = 20
XP_WEEKLY_TASK = 100
XP_TASK_MINOR = 10
XP_TASK_RECOVERY = 10
XP_WEEK_GOAL = 50

MAX_COUNTED_WORKOUTS_PER_DAY = 2
MAX_COUNTED_SETS_PER_WORKOUT = 30

# Для перехода с уровня N на N+1 нужно XP_PER_LEVEL_BASE * N очков.
XP_PER_LEVEL_BASE = 100

# --- Характеристики ---
STAT_BY_CATEGORY = {"strength": "strength", "cardio": "endurance", "mobility": "agility"}
STAT_PER_SET = 1
DISCIPLINE_PER_WORKOUT = 1
DISCIPLINE_PER_WEEK_CLOSED = 5

# --- Серии ---
FREEZES_PER_MONTH = 1

# --- Источники XP в журнале ---
SRC_WORKOUT = "workout"
SRC_SETS = "sets"
SRC_TASK = "task"
SRC_WEEK_GOAL = "week_goal"
SRC_WEIGHT = "weight"

# --- Задания: условия хранятся как данные (metric + target) ---
TASK_PERIODS = ("daily", "weekly")
TASK_KINDS = ("main", "minor", "recovery")
# manual — подтверждается явно (задание восстановления), остальные считаются по журналу.
TASK_METRICS = ("workouts_finished", "sets_logged", "weight_entries", "manual")
TASK_TEMPLATES = (
    {"code": "daily_workout", "period": "daily", "kind": "main", "metric": "workouts_finished",
     "target": 1, "xp_reward": XP_DAILY_TASK},
    {"code": "daily_weight", "period": "daily", "kind": "minor", "metric": "weight_entries",
     "target": 1, "xp_reward": XP_TASK_MINOR},
    {"code": "daily_recovery", "period": "daily", "kind": "recovery", "metric": "manual",
     "target": 1, "xp_reward": XP_TASK_RECOVERY},
    {"code": "weekly_workouts_3", "period": "weekly", "kind": "main",
     "metric": "workouts_finished", "target": 3, "xp_reward": XP_WEEKLY_TASK},
    {"code": "weekly_sets_40", "period": "weekly", "kind": "minor", "metric": "sets_logged",
     "target": 40, "xp_reward": XP_WEEKLY_TASK},
)

# --- Ранги: код и минимальный уровень (стартовые границы, подлежат пересмотру по данным MVP) ---
RANKS = (
    ("novice", 1),
    ("amateur", 10),
    ("practitioner", 20),
    ("athlete", 30),
    ("master", 40),
    ("expert", 50),
)
LEVEL_POINTS_PER_LEVEL = 1

# --- Режим пользователя ---
USER_MODES = ("active", "paused")

# --- Достижения: код, метрика (из статистики пользователя) и порог ---
ACHIEVEMENTS = (
    {"code": "first_workout", "metric": "workouts", "target": 1},
    {"code": "workouts_10", "metric": "workouts", "target": 10},
    {"code": "workouts_50", "metric": "workouts", "target": 50},
    {"code": "sets_100", "metric": "sets", "target": 100},
    {"code": "streak_4", "metric": "streak_weeks", "target": 4},
    {"code": "streak_12", "metric": "streak_weeks", "target": 12},
    {"code": "tasks_30", "metric": "tasks", "target": 30},
    {"code": "level_10", "metric": "level", "target": 10},
)

# --- Вес ---
MIN_WEIGHT_KG = 20
MAX_WEIGHT_KG = 500
MAX_WEIGHT_BACKDATE_DAYS = 365
DEFAULT_WEIGHT_RANGE_DAYS = 90

# --- Напоминания ---
DEFAULT_REMINDER_TIME = "19:00"
# Окно после заданного времени, в котором напоминание ещё можно отправить
# (на случай, если бот был недоступен).
REMINDER_WINDOW_MIN = 180
# Сколько напоминаний в сутки можно отправить одному пользователю.
MAX_REMINDERS_PER_DAY = 1

# --- ИИ-корректировка ---
# Итоговое решение по тренировке. Его принимает движок (app/engine); первые четыре значения
# выдаёт он, остальные остались в старых записях журнала.
AI_DECISIONS = (
    "increase_weight",
    "keep_weight",
    "reduce_weight",
    "deload",
    "change_volume",
    "replace_exercise",
    "change_rep_range",
)
# История и плато.
AI_HISTORY_SESSIONS = 6  # сколько прошлых тренировок по упражнению видит модель
AI_PAST_DECISIONS = 5  # сколько прошлых рекомендаций (с оценками) видит модель
PLATEAU_MIN_SESSIONS = 4  # меньше тренировок — плато не определяем
PLATEAU_SESSIONS_WITHOUT_GAIN = 3  # столько тренировок подряд без нового лучшего результата
PLATEAU_TOLERANCE = 0.01  # прирост меньше 1% считаем отсутствием роста
PROGRESS_POINTS = 20  # точек на графике прогрессии по упражнению
# Самочувствие перед тренировкой (1-5): при таком значении и ниже нагрузку не повышаем.
LOW_READINESS_MAX = 2
# Стартовый план первой тренировки.
STARTER_SETS = 3
STARTER_REPS = {
    "strength": 5,
    "strength_mass": 6,
    "mass": 8,
    "return": 10,
    "weight_loss": 12,
    "general": 10,
    "shape": 10,
}
STARTER_DEFAULT_REPS = 10
STARTER_MAX_EXERCISES = 5
STARTER_DEFAULT_MUSCLES = ("legs", "chest", "back", "shoulders", "core")
# Упражнения с собственным весом: подходят дома и без оборудования.
BODYWEIGHT_EXERCISES = ("Отжимания", "Подтягивания", "Выпады", "Скручивания")
AI_ADJUSTS_PER_DAY = 10  # лимит вызовов ИИ на пользователя в сутки
COACH_MAX_RULES_IN_PROMPT = 30  # сколько одобренных правил тренера попадает в запрос к модели
COACH_MIN_FEEDBACK_TO_LEARN = 20  # сколько оценок нужно, чтобы ИИ предлагал правила
COACH_MAX_PROPOSALS = 3
AI_MAX_WEIGHT_INCREASE_PCT = 0.10  # нагрузку наращиваем постепенно
AI_MIN_WEIGHT_STEP_KG = 2.5  # но шаг в 2,5 кг допустим всегда
AI_MAX_EXERCISES = 8
AI_MAX_SETS = 8
AI_MAX_REPS = 30
AI_MAX_CHANGES = 6
AI_MAX_TEXT_LEN = 1200
AI_MAX_NOTES_LEN = 2000
AI_ALTERNATIVES_PER_EXERCISE = 5
