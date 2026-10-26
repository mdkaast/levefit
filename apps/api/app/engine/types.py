"""Типы данных движка. Всё неизменяемое и не зависит от БД и сети."""

from dataclasses import dataclass, field
from datetime import date
from typing import Literal

Action = Literal["increase", "hold", "reduce", "reset", "deload"]


@dataclass(frozen=True)
class SetResult:
    weight_kg: float | None
    reps: int | None
    rir: int | None = None


@dataclass(frozen=True)
class PlanTarget:
    """План на упражнение; reps — верх диапазона повторений."""

    weight_kg: float | None
    sets: int
    reps: int


@dataclass(frozen=True)
class SessionSummary:
    """Прошлая тренировка по упражнению (без сегодняшней)."""

    day: date
    top_weight_kg: float | None
    score: float  # расчётный максимум; для упражнений без веса — повторы
    sets: tuple[SetResult, ...] = ()


@dataclass(frozen=True)
class ExerciseInput:
    exercise_id: int
    name: str
    muscle_group: str
    sets: tuple[SetResult, ...]
    plan: PlanTarget | None = None
    history: tuple[SessionSummary, ...] = ()
    step_kg: float | None = None  # шаг инвентаря; по умолчанию определяется по группе мышц
    plateau: bool = False  # признак плато по истории (считается вне движка)


@dataclass(frozen=True)
class Context:
    experience: str | None = None  # beginner | intermediate | advanced
    goal: str | None = None
    age: int | None = None
    health_flag: bool = False  # в заметках боль или тревожные симптомы
    low_readiness: bool = False  # плохое самочувствие перед этой тренировкой
    recent_low_readiness: int = 0  # сколько прошлых тренировок были «лёгкими днями»
    deload_due: bool = False  # плановая разгрузка по календарю


@dataclass(frozen=True)
class ExerciseDecision:
    exercise_id: int
    name: str
    action: Action
    rule: str  # идентификатор сработавшего правила (для журнала и проверки объяснений)
    reason: str  # короткая фактическая причина по-русски
    from_weight_kg: float | None
    next_weight_kg: float | None
    next_sets: int
    next_reps: tuple[int, ...]  # цель по повторениям на каждый подход
    rep_max: int  # верх диапазона повторений: именно он идёт в план на следующий раз
    target_rir: int
    flags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SessionDecision:
    rules_version: str
    overall: Literal["increase_weight", "keep_weight", "reduce_weight", "deload"]
    exercises: tuple[ExerciseDecision, ...]
    deload_signals: tuple[str, ...] = ()
