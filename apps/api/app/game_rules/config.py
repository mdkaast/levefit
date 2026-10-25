"""Единый конфиг игровых констант. Стартовые значения, подлежат подтверждению владельцем."""

APPEARANCES = ("warrior", "runner", "sage")
GOALS = ("mass", "strength", "shape")
EQUIPMENT = ("gym", "home", "none")

DEFAULT_WORKOUTS_PER_WEEK = 3
MIN_WORKOUTS_PER_WEEK = 1
MAX_WORKOUTS_PER_WEEK = 7

CHARACTER_NAME_MAX_LEN = 30

EXERCISE_CATEGORIES = ("strength", "cardio", "mobility")
WORKOUT_STATUSES = ("planned", "in_progress", "finished")

# --- XP (стартовые значения, подтверждены владельцем) ---
XP_WORKOUT = 50
XP_PER_SET = 5
XP_WEIGHT_ENTRY = 5  # начисляется на этапе 4
XP_DAILY_QUEST = 20
XP_WEEKLY_QUEST = 100
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
SRC_QUEST_DAILY = "quest_daily"
SRC_QUEST_WEEKLY = "quest_weekly"
SRC_WEEK_GOAL = "week_goal"

# --- Квесты: условия хранятся как данные (metric + target) ---
QUEST_METRICS = ("workouts_finished", "sets_logged")
QUEST_TEMPLATES = (
    {"code": "daily_workout", "kind": "daily", "metric": "workouts_finished", "target": 1,
     "xp_reward": XP_DAILY_QUEST},
    {"code": "daily_sets_10", "kind": "daily", "metric": "sets_logged", "target": 10,
     "xp_reward": XP_DAILY_QUEST},
    {"code": "weekly_workouts_3", "kind": "weekly", "metric": "workouts_finished", "target": 3,
     "xp_reward": XP_WEEKLY_QUEST},
    {"code": "weekly_sets_40", "kind": "weekly", "metric": "sets_logged", "target": 40,
     "xp_reward": XP_WEEKLY_QUEST},
)
