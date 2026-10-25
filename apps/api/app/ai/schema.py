"""Схема ответа ИИ-корректировки. Числовые и текстовые ограничения проверяет safety.py."""

from typing import Literal

from pydantic import BaseModel


class NextExercise(BaseModel):
    exercise_id: int
    name: str
    target_weight_kg: float | None
    sets: int
    reps: int


class Adjustment(BaseModel):
    # Что изменилось по сравнению с планом (простыми фразами).
    changes: list[str]
    decision: Literal["keep_weight", "reduce_weight", "change_volume", "replace_exercise"]
    next_workout: list[NextExercise]
    # Объяснение решения простым языком.
    rationale: str


class AdjustmentOut(Adjustment):
    """Ответ API: решение ИИ и признак того, что в заметках упомянуты боль или травма."""

    health_flag: bool = False


class PlanOut(BaseModel):
    """План следующей тренировки из последнего решения ИИ."""

    workout_id: int | None
    items: list[NextExercise]
