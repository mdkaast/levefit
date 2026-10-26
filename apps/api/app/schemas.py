from datetime import date as date_type
from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, computed_field, field_validator

from app.game_rules import config as rules
from app.game_rules.levels import level_from_total_xp, xp_for_next_level
from app.game_rules.reminders import parse_hhmm

Appearance = Literal[rules.APPEARANCES]  # type: ignore[valid-type]
Goal = Literal[rules.GOALS]  # type: ignore[valid-type]
Equipment = Literal[rules.EQUIPMENT]  # type: ignore[valid-type]


class AuthRequest(BaseModel):
    init_data: str = Field(min_length=1, max_length=4096)


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int


Gender = Literal[rules.GENDERS]  # type: ignore[valid-type]
Experience = Literal[rules.EXPERIENCE_LEVELS]  # type: ignore[valid-type]
Lifestyle = Literal[rules.LIFESTYLES]  # type: ignore[valid-type]
Muscle = Literal[rules.TARGET_MUSCLES]  # type: ignore[valid-type]
Silhouette = Literal["male", "female"]


class CharacterCreate(BaseModel):
    name: str = Field(max_length=rules.CHARACTER_NAME_MAX_LEN)
    gender: Gender | None = None
    age: int | None = Field(default=None, ge=rules.MIN_AGE, le=rules.MAX_AGE)
    height_cm: int | None = Field(default=None, ge=rules.MIN_HEIGHT_CM, le=rules.MAX_HEIGHT_CM)
    # Стартовый вес попадает в график веса (без XP).
    weight_kg: float | None = Field(default=None, ge=rules.MIN_WEIGHT_KG, le=rules.MAX_WEIGHT_KG)
    experience: Experience | None = None
    lifestyle: Lifestyle | None = None
    target_muscles: list[Muscle] = Field(default_factory=list, max_length=len(rules.TARGET_MUSCLES))
    silhouette: Silhouette | None = None
    appearance: Appearance = rules.APPEARANCES[0]
    goal: Goal | None = None
    workouts_per_week: int = Field(
        default=rules.DEFAULT_WORKOUTS_PER_WEEK,
        ge=rules.MIN_WORKOUTS_PER_WEEK,
        le=rules.MAX_WORKOUTS_PER_WEEK,
    )
    equipment: Equipment = "gym"

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value

    @field_validator("target_muscles")
    @classmethod
    def muscles_unique(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))


class CharacterPatch(BaseModel):
    """Изменение профиля персонажа после регистрации: акцент на мышцы (B5) и силуэт (B9)."""

    target_muscles: list[Muscle] | None = Field(default=None, max_length=len(rules.TARGET_MUSCLES))
    silhouette: Silhouette | None = None

    @field_validator("target_muscles")
    @classmethod
    def muscles_unique(cls, value: list[str] | None) -> list[str] | None:
        return list(dict.fromkeys(value)) if value is not None else None


class CharacterOut(BaseModel):
    model_config = {"from_attributes": True}

    name: str
    level: int
    rank: str
    level_points: int
    xp: int
    strength: int
    endurance: int
    agility: int
    discipline: int
    appearance: str
    goal: str | None
    workouts_per_week: int
    equipment: str
    gender: str | None
    age: int | None
    height_cm: int | None
    experience: str | None
    lifestyle: str | None
    target_muscles: list[str] | None
    silhouette: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def xp_in_level(self) -> int:
        return level_from_total_xp(self.xp)[1]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def xp_to_next(self) -> int:
        return xp_for_next_level(self.level)


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str | None
    locale: str | None
    mode: str
    reminders_enabled: bool
    reminder_time: str
    timezone: str | None


class UserPatch(BaseModel):
    """Частичное обновление настроек: не переданные поля не меняются."""

    reminders_enabled: bool | None = None
    mode: Literal["active", "paused"] | None = None
    reminder_time: str | None = None
    timezone: str | None = Field(default=None, max_length=64)

    @field_validator("reminder_time")
    @classmethod
    def valid_time(cls, value: str | None) -> str | None:
        if value is not None:
            parse_hhmm(value)
        return value

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                ZoneInfo(value)
            except (ZoneInfoNotFoundError, ValueError):
                raise ValueError("unknown timezone") from None
        return value


class StreakOut(BaseModel):
    weeks: int
    freezes_left: int
    week_workouts: int
    weekly_goal: int


class MeOut(BaseModel):
    user: UserOut
    is_admin: bool = False
    character: CharacterOut | None
    streak: StreakOut | None


ExerciseCategory = Literal[rules.EXERCISE_CATEGORIES]  # type: ignore[valid-type]
WorkoutStatus = Literal[rules.WORKOUT_STATUSES]  # type: ignore[valid-type]


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    category: ExerciseCategory
    muscle_group: str = Field(min_length=1, max_length=32)

    @field_validator("name", "muscle_group")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class ExerciseOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    category: str
    muscle_group: str
    owner_id: int | None


class WorkoutCreate(BaseModel):
    title: str = Field(default="Тренировка", max_length=80)
    date: date_type | None = None
    status: Literal["planned", "in_progress"] = "in_progress"
    notes: str | None = Field(default=None, max_length=2000)
    sleep_quality: int | None = Field(default=None, ge=1, le=5)
    energy: int | None = Field(default=None, ge=1, le=5)
    pain: bool = False


class WorkoutFinish(BaseModel):
    duration_min: int | None = Field(default=None, ge=1, le=1440)
    notes: str | None = Field(default=None, max_length=2000)


class SetCreate(BaseModel):
    exercise_id: int
    weight_kg: float | None = Field(default=None, ge=0, le=1000)
    reps: int | None = Field(default=None, ge=1, le=1000)
    rir: int | None = Field(default=None, ge=0, le=10)
    duration_s: int | None = Field(default=None, ge=1, le=86400)
    distance_m: int | None = Field(default=None, ge=1, le=1_000_000)
    # Ключ идемпотентности от клиента: повторная отправка того же подхода не создаёт дубль.
    client_id: str | None = Field(default=None, min_length=8, max_length=36)


class SetOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    exercise_id: int
    set_no: int
    weight_kg: float | None
    reps: int | None
    rir: int | None
    duration_s: int | None
    distance_m: int | None


class WorkoutSummary(BaseModel):
    id: int
    date: date_type
    title: str
    status: str
    duration_min: int | None
    sets_count: int


class WorkoutOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    date: date_type
    title: str
    status: str
    duration_min: int | None
    notes: str | None
    sets: list[SetOut]


class RewardOut(BaseModel):
    counted: bool
    xp_gained: int
    workout_xp: int
    sets_xp: int
    task_xp: int
    week_xp: int
    weight_xp: int
    level_before: int
    level_after: int
    leveled_up: bool
    rank_before: str
    rank_after: str
    rank_changed: bool
    level_points_gained: int
    stat_gains: dict[str, int]
    tasks_completed: list[str]
    achievements_earned: list[str]
    week_closed: bool
    streak_weeks: int


class FinishOut(WorkoutOut):
    reward: RewardOut


class TaskOut(BaseModel):
    id: int
    code: str
    period: str
    kind: str
    progress: int
    target: int
    xp_reward: int
    status: str


class AchievementOut(BaseModel):
    code: str
    earned: bool
    earned_at: datetime | None
    progress: int
    target: int


class PlanItem(BaseModel):
    exercise_id: int
    weight_kg: float | None = Field(default=None, ge=0, le=1000)
    sets: int = Field(ge=1, le=20)
    reps: int = Field(ge=1, le=1000)


class AdjustRequest(BaseModel):
    """Необязательный план тренировки; без него берётся прошлая рекомендация ИИ."""

    plan: list[PlanItem] | None = Field(default=None, max_length=30)
