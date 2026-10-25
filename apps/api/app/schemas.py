from datetime import date as date_type
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


class CharacterCreate(BaseModel):
    name: str = Field(max_length=rules.CHARACTER_NAME_MAX_LEN)
    appearance: Appearance
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


class CharacterOut(BaseModel):
    model_config = {"from_attributes": True}

    name: str
    level: int
    xp: int
    strength: int
    endurance: int
    agility: int
    discipline: int
    appearance: str
    goal: str | None
    workouts_per_week: int
    equipment: str

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
    reminders_enabled: bool
    reminder_time: str
    timezone: str | None


class UserPatch(BaseModel):
    """Частичное обновление настроек: не переданные поля не меняются."""

    reminders_enabled: bool | None = None
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


class WorkoutFinish(BaseModel):
    duration_min: int | None = Field(default=None, ge=1, le=1440)


class SetCreate(BaseModel):
    exercise_id: int
    weight_kg: float | None = Field(default=None, ge=0, le=1000)
    reps: int | None = Field(default=None, ge=1, le=1000)
    rir: int | None = Field(default=None, ge=0, le=10)
    duration_s: int | None = Field(default=None, ge=1, le=86400)
    distance_m: int | None = Field(default=None, ge=1, le=1_000_000)


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
    quest_xp: int
    week_xp: int
    level_before: int
    level_after: int
    leveled_up: bool
    quests_completed: list[str]
    week_closed: bool
    streak_weeks: int


class FinishOut(WorkoutOut):
    reward: RewardOut


class QuestOut(BaseModel):
    id: int
    code: str
    kind: str
    progress: int
    target: int
    xp_reward: int
    status: str
