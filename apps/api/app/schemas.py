from datetime import date as date_type
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.game_rules import config as rules

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


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str | None
    locale: str | None


class MeOut(BaseModel):
    user: UserOut
    character: CharacterOut | None


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
