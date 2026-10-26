"""Объяснение решения движка без ИИ: шаблон на случай, когда ИИ-тренер недоступен.

ИИ-тренер формулирует то же самое живее, но числа берёт отсюда же: любое название веса
в его тексте проверяется по `allowed_weights`.
"""

from app.engine.types import SessionDecision

_OVERALL = {
    "increase_weight": (
        "Подходы выполнены на верхней границе диапазона, поэтому вес повышается на один шаг. "
        "Там, где прогресс ещё не заработан, вес сохраняется."
    ),
    "keep_weight": (
        "Прогресс по весу пока не заработан: вес сохраняем, а подходам, которые отстали, "
        "ставим цель на один повтор выше."
    ),
    "reduce_weight": (
        "Нагрузка оказалась тяжелее плана, поэтому на следующей тренировке вес снижается. "
        "Это временный шаг назад, чтобы продолжить набор повторений без перегрузки."
    ),
    "deload": (
        "Это разгрузка: подходов меньше, вес сохраняется, запас повторений больше. "
        "Так организм восстанавливается, а прогресс не теряется."
    ),
}

_PAIN = (
    " Вы упомянули боль или необычные ощущения: нагрузка не растёт. "
    "Если дискомфорт сохраняется, обратитесь к врачу или физиотерапевту."
)


def template_explanation(session: SessionDecision, *, health_flag: bool) -> tuple[list[str], str]:
    """Короткие факты (по одному на упражнение) и объяснение из двух-трёх предложений."""
    changes = [d.reason for d in session.exercises][:6]
    rationale = _OVERALL[session.overall]
    if any("plateau" in d.flags for d in session.exercises):
        rationale += " Результат по части упражнений не растёт несколько тренировок подряд."
    if health_flag:
        rationale += _PAIN
    return changes, rationale


def allowed_weights(session: SessionDecision, steps: dict[int, float] | None = None) -> set[float]:
    """Веса, которые можно называть в тексте: сегодняшние, следующие и разница между ними."""
    allowed: set[float] = set()
    for d in session.exercises:
        for value in (d.from_weight_kg, d.next_weight_kg):
            if value is not None:
                allowed.add(round(value, 2))
        if d.from_weight_kg is not None and d.next_weight_kg is not None:
            allowed.add(round(abs(d.next_weight_kg - d.from_weight_kg), 2))
        if steps and d.exercise_id in steps:
            allowed.add(steps[d.exercise_id])
    return allowed


def describe(session: SessionDecision) -> list[dict]:
    """Решения движка в виде словарей для ИИ-тренера и журнала."""
    return [
        {
            "exercise_id": d.exercise_id,
            "name": d.name,
            "action": d.action,
            "rule": d.rule,
            "reason": d.reason,
            "from_weight_kg": d.from_weight_kg,
            "next_weight_kg": d.next_weight_kg,
            "next_sets": d.next_sets,
            "next_reps": list(d.next_reps),
            "rep_max": d.rep_max,
            "target_rir": d.target_rir,
            "flags": list(d.flags),
        }
        for d in session.exercises
    ]
