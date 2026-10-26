"""Схемы решения о нагрузке. Числа даёт движок (app/engine), ИИ-тренер пишет только текст."""

from typing import Literal

from pydantic import BaseModel


class NextExercise(BaseModel):
    exercise_id: int
    name: str
    target_weight_kg: float | None
    sets: int
    reps: int  # верх диапазона повторений
    # Цель по повторениям на каждый подход (например, 8/8/7); пусто у старых записей.
    rep_targets: list[int] | None = None


class Adjustment(BaseModel):
    # Что изменилось по сравнению с планом (простыми фразами).
    changes: list[str]
    decision: Literal[
        "increase_weight",
        "keep_weight",
        "reduce_weight",
        "change_volume",
        "replace_exercise",
        "deload",
        "change_rep_range",
    ]
    next_workout: list[NextExercise]
    # Объяснение решения простым языком.
    rationale: str


class Explanation(BaseModel):
    """Что ИИ-тренер пишет по решению движка: короткие факты и объяснение простым языком."""

    changes: list[str]
    rationale: str


class EngineDecisionOut(BaseModel):
    """Решение движка по упражнению: что, по какому правилу и почему."""

    exercise_id: int
    name: str
    action: str
    rule: str
    reason: str
    from_weight_kg: float | None
    next_weight_kg: float | None
    flags: list[str] = []


class AdjustmentOut(Adjustment):
    """Ответ API: решение движка, объяснение и признак боли или травмы в заметках."""

    health_flag: bool = False
    engine_version: str | None = None
    explained_by: Literal["llm", "template"] | None = None
    engine: list[EngineDecisionOut] = []


class PlanOut(BaseModel):
    """План следующей тренировки: последнее решение движка или стартовый план."""

    workout_id: int | None
    items: list[NextExercise]
    source: Literal["ai", "starter"] | None = None
    # Поправки к плану перед тренировкой (например, после перерыва), простыми фразами.
    notes: list[str] = []


class RuleProposals(BaseModel):
    """Предложения новых правил тренера; в работу попадают только после одобрения владельцем."""

    rules: list[str]
