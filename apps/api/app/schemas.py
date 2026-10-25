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
