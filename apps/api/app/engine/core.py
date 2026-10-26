"""Детерминированный движок решений: что делать с нагрузкой на следующей тренировке.

Чистые функции без БД и сети. Правила описаны в `rules.py` и `data/programming_rules.md`.
ИИ-тренер числа не меняет: он только объясняет решение, которое вернул этот модуль.
"""

import math

from app.engine import rules as R
from app.engine.types import (
    Context,
    ExerciseDecision,
    ExerciseInput,
    SessionDecision,
    SetResult,
)

# ---------- округление и формат ----------


def _r2(value: float) -> float:
    return round(value + 1e-9, 2)


def round_to_step(weight: float, step: float) -> float:
    """Ближайший вес, кратный шагу инвентаря (72 кг при шаге 2,5 → 72,5)."""
    return _r2(math.floor(weight / step + 0.5) * step)


def kg(value: float | None) -> str:
    """«80» или «82,5» для текстов."""
    if value is None:
        return "свой вес"
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def estimate_one_rep_max(weight: float | None, reps: int | None) -> float:
    """Epley: w × (1 + reps/30). Без веса или повторов — 0 (такие подходы оцениваем повторами)."""
    if not weight or not reps:
        return 0.0
    return weight * (1 + reps / 30)


def session_score(sets: tuple[SetResult, ...]) -> float:
    best = max((estimate_one_rep_max(s.weight_kg, s.reps) for s in sets), default=0.0)
    if best > 0:
        return round(best, 1)
    return float(max((s.reps or 0 for s in sets), default=0))


# ---------- параметры по контексту ----------


def step_for(item: ExerciseInput, ctx: Context) -> float:
    if item.step_kg:
        return item.step_kg
    if item.muscle_group in R.LOWER_BODY_GROUPS and ctx.experience == "beginner":
        return R.LOWER_BODY_BEGINNER_STEP_KG
    return R.DEFAULT_STEP_KG


def target_rir(ctx: Context, extra: int = 0) -> int:
    base = R.TARGET_RIR
    if ctx.experience == "beginner":
        base = max(base, R.BEGINNER_MIN_TARGET_RIR)
    return base + extra


def _hold_targets(
    done: list[SetResult], planned_sets: int, rep_min: int, rep_max: int
) -> tuple[int, ...]:
    """Цель по повторениям на следующий раз: отстающим подходам +1 (пример 8/7/6 → 8/8/7)."""
    targets = [
        min(rep_max, (s.reps or 0) + 1) if (s.reps or 0) < rep_max else rep_max for s in done
    ]
    targets += [rep_min] * max(0, planned_sets - len(targets))
    return tuple(targets[:planned_sets])


# ---------- решение по одному упражнению ----------


def decide_exercise(
    item: ExerciseInput, ctx: Context, *, deload: str | None = None
) -> ExerciseDecision:
    done = [s for s in item.sets if s.reps is not None]
    weights = [s.weight_kg for s in done if s.weight_kg]
    w = max(weights) if weights else None
    planned_sets = item.plan.sets if item.plan else max(len(done), 1)
    rep_max = (
        item.plan.reps
        if item.plan
        else R.DEFAULT_TOP_REPS.get(ctx.goal or "", R.DEFAULT_TOP_REPS_FALLBACK)
    )
    rep_min = max(1, rep_max - R.DOUBLE_PROGRESSION_SPAN)
    rir_target = target_rir(ctx)
    step = step_for(item, ctx)

    flags: list[str] = []
    if item.plateau:
        flags.append("plateau")
    if ctx.low_readiness:
        flags.append("low_readiness")
    if ctx.health_flag:
        flags.append("pain")

    def build(action, rule, reason, next_w, next_sets, reps, rir=rir_target, top=rep_max):
        return ExerciseDecision(
            exercise_id=item.exercise_id,
            name=item.name,
            action=action,
            rule=rule,
            reason=reason,
            from_weight_kg=w,
            next_weight_kg=next_w,
            next_sets=next_sets,
            next_reps=tuple(reps),
            rep_max=top,
            target_rir=rir,
            flags=tuple(flags),
        )

    if not done:
        return build(
            "hold",
            "no_data.hold",
            f"{item.name}: подходов с повторами нет, нагрузку не меняем.",
            w,
            planned_sets,
            [rep_min] * planned_sets,
        )

    # Боль или тревожные симптомы: нагрузка не растёт, вес снижается (6.3)
    if ctx.health_flag:
        sets_next = min(planned_sets, len(done))
        if w is None:
            return build(
                "hold",
                "pain.hold",
                f"{item.name}: есть жалоба на боль, объём не увеличиваем.",
                None,
                sets_next,
                [min(rep_max, s.reps or rep_min) for s in done][:sets_next],
            )
        lowered = round_to_step(w * (1 - R.PAIN_REDUCE_PCT), step)
        if lowered >= w:
            lowered = _r2(max(0.0, w - step))
        return build(
            "reduce",
            "pain.reduce",
            f"{item.name}: есть жалоба на боль, вес снижаем с {kg(w)} до {kg(lowered)} кг.",
            lowered,
            sets_next,
            [rep_min] * sets_next,
            rir_target + 1,
        )

    # Разгрузка: подходов меньше, вес сохраняем, запас повторений больше (4.4)
    if deload:
        sets_next = max(1, math.ceil(planned_sets * R.DELOAD_SETS_FACTOR))
        why = (
            "накопились признаки усталости"
            if deload == "reactive"
            else "подошёл срок плановой разгрузки"
        )
        return build(
            "deload",
            f"deload.{deload}",
            f"{item.name}: {why}; подходов {sets_next} вместо {planned_sets}, вес {kg(w)} кг сохраняем.",
            w,
            sets_next,
            [rep_min] * sets_next,
            rir_target + R.DELOAD_RIR_PLUS,
        )

    all_done = len(done) >= planned_sets
    all_top = all_done and all(s.reps >= rep_max for s in done if s.reps is not None)
    failed = any(s.reps < rep_min for s in done if s.reps is not None)
    last_rir = next((s.rir for s in reversed(done) if s.rir is not None), None)
    gap_low = (rir_target - last_rir) if last_rir is not None else 0
    gap_high = (last_rir - rir_target) if last_rir is not None else 0

    # Упражнение с собственным весом: растут повторения (4.3)
    if w is None:
        if all_top and not ctx.low_readiness:
            top = min(R.BODYWEIGHT_TOP_CAP, rep_max + 1)
            return build(
                "increase",
                "bodyweight.increase",
                f"{item.name}: все подходы на {rep_max} повторах, цель повышаем до {top}.",
                None,
                planned_sets,
                [top] * planned_sets,
                top=top,
            )
        reps = _hold_targets(done, planned_sets, rep_min, rep_max)
        return build(
            "hold",
            "bodyweight.hold",
            f"{item.name}: цель {rep_max} повторов в каждом подходе пока не достигнута.",
            None,
            planned_sets,
            list(reps),
        )

    hold_reps = list(_hold_targets(done, planned_sets, rep_min, rep_max))

    # Плохое самочувствие: прибавки нет, неудачи не засчитываем
    if ctx.low_readiness:
        return build(
            "hold",
            "readiness.hold",
            f"{item.name}: самочувствие было низким, вес {kg(w)} кг сохраняем без выводов о прогрессе.",
            w,
            planned_sets,
            hold_reps,
        )

    # Подход закончен значительно тяжелее целевого RIR: −4% за каждое «лишнее» повторение
    if gap_low >= R.RIR_GAP_TRIGGER:
        lowered = round_to_step(w * (1 - R.RIR_ADJUST_PCT * gap_low), step)
        if lowered >= w:
            lowered = _r2(max(0.0, w - step))
        return build(
            "reduce",
            "rir.too_hard",
            f"{item.name}: последний подход дался тяжелее плана (запас {last_rir} при цели {rir_target}), "
            f"вес снижаем с {kg(w)} до {kg(lowered)} кг.",
            lowered,
            planned_sets,
            hold_reps,
        )

    # Оценка «Тяжело»: повторы выполнены, но упражнение на пределе: вес не повышаем
    if all_top and item.rating == "hard":
        return build(
            "hold",
            "rating.hold",
            f"{item.name}: оценка «Тяжело», вес {kg(w)} кг сохраняем, пока упражнение не станет легче.",
            w,
            planned_sets,
            hold_reps,
        )

    # Двойная прогрессия: все подходы на верхней границе при целевом RIR → вес + шаг
    # (оценка «Легко» разрешает прибавку, даже если запас сил не указан или чуть меньше цели)
    if all_top and (last_rir is None or last_rir >= rir_target or item.rating == "easy"):
        steps = 1
        if gap_high >= R.RIR_GAP_TRIGGER:
            steps = max(1, min(R.RIR_MAX_UP_STEPS, round(w * R.RIR_ADJUST_PCT * gap_high / step)))
        cap = max(w * (1 + R.MAX_GAIN_PCT), w + step)
        while steps > 1 and w + steps * step > cap + 1e-9:
            steps -= 1
        new_w = _r2(w + steps * step)
        return build(
            "increase",
            "double_progression.increase",
            f"{item.name}: все подходы на {rep_max} повторах, вес повышаем с {kg(w)} до {kg(new_w)} кг.",
            new_w,
            planned_sets,
            [rep_min] * planned_sets,
        )

    if failed:
        prev = item.history[-1] if item.history else None
        prev_failed = bool(
            prev
            and prev.top_weight_kg
            and abs(prev.top_weight_kg - w) <= R.SAME_WEIGHT_TOLERANCE_KG
            and any(s.reps is not None and s.reps < rep_min for s in prev.sets)
        )
        if prev_failed:
            if ctx.goal == "weight_loss" and ctx.experience != "beginner":
                return build(
                    "hold",
                    "deficit.hold",
                    f"{item.name}: при снижении веса удержание {kg(w)} кг считается успехом, вес не сбрасываем.",
                    w,
                    planned_sets,
                    hold_reps,
                )
            lowered = round_to_step(w * (1 - R.RESET_PCT), step)
            if lowered >= w:
                lowered = _r2(max(0.0, w - step))
            return build(
                "reset",
                "stall.reset",
                f"{item.name}: цель по повторениям не выполнена второй раз подряд на {kg(w)} кг, "
                f"возвращаемся к {kg(lowered)} кг и набираем заново.",
                lowered,
                planned_sets,
                [rep_min] * planned_sets,
            )
        return build(
            "hold",
            "hold.first_miss",
            f"{item.name}: часть подходов ниже {rep_min} повторов; на одну неудачную тренировку "
            f"не реагируем, вес {kg(w)} кг сохраняем.",
            w,
            planned_sets,
            hold_reps,
        )

    reason = f"{item.name}: вес {kg(w)} кг сохраняем, отстающим подходам цель +1 повтор."
    rule = "double_progression.hold"
    if all_top and last_rir is not None and last_rir < rir_target:
        reason = f"{item.name}: повторы выполнены, но запас сил меньше целевого ({last_rir} вместо {rir_target}), вес {kg(w)} кг сохраняем."
        rule = "double_progression.hold_rir"
    elif not all_done:
        reason = f"{item.name}: выполнено {len(done)} из {planned_sets} подходов, вес {kg(w)} кг сохраняем."
        rule = "double_progression.hold_incomplete"
    return build("hold", rule, reason, w, planned_sets, hold_reps)


# ---------- решение по тренировке ----------


def deload_signals(items: tuple[ExerciseInput, ...], ctx: Context) -> tuple[str, ...]:
    """Сигналы реактивной разгрузки (4.4): достаточно двух из них."""
    signals: list[str] = []
    for item in items:
        scores = [h.score for h in item.history] + [session_score(item.sets)]
        if len(scores) >= 3:
            best_before = max(scores[:-2])
            floor = best_before * (1 - R.DELOAD_E1RM_DROP)
            if best_before > 0 and scores[-1] < floor and scores[-2] < floor:
                signals.append("e1rm_drop")
                break
    if ctx.health_flag:
        signals.append("pain")
    if ctx.recent_low_readiness + (1 if ctx.low_readiness else 0) >= R.DELOAD_LOW_READINESS_COUNT:
        signals.append("poor_recovery")
    if ctx.recent_skips >= R.DELOAD_SKIPS_COUNT:
        signals.append("skips")
    return tuple(signals)


def decide_session(items: tuple[ExerciseInput, ...], ctx: Context) -> SessionDecision:
    signals = deload_signals(items, ctx)
    deload: str | None = None
    if len(signals) >= R.DELOAD_SIGNALS_REQUIRED:
        deload = "reactive"
    elif ctx.deload_due:
        deload = "scheduled"

    decisions = tuple(decide_exercise(item, ctx, deload=deload) for item in items)
    actions = {d.action for d in decisions}
    if "deload" in actions:
        overall = "deload"
    elif actions & {"reduce", "reset"}:
        overall = "reduce_weight"
    elif "increase" in actions:
        overall = "increase_weight"
    else:
        overall = "keep_weight"
    return SessionDecision(
        rules_version=R.RULES_VERSION,
        overall=overall,
        exercises=decisions,
        deload_signals=signals,
    )


# ---------- поправки к плану перед тренировкой ----------


def return_factors(days_since_last: int | None, age: int | None) -> tuple[float, float, bool]:
    """После перерыва: (снижение веса, множитель объёма, нужна ли тестовая сессия). 4.5."""
    if days_since_last is None or days_since_last <= R.RETURN_TABLE[0][0]:
        return 0.0, 1.0, False
    index = next(i for i, row in enumerate(R.RETURN_TABLE) if days_since_last <= row[0])
    if age is not None and age > R.RETURN_AGE_SHIFT_FROM:
        index = min(index + 1, len(R.RETURN_TABLE) - 1)
    _, weight_pct, volume = R.RETURN_TABLE[index]
    return weight_pct, volume, days_since_last > R.RETURN_RECALIBRATE_AFTER_DAYS


def apply_return(
    weight: float | None, sets: int, step: float, weight_pct: float, volume: float
) -> tuple[float | None, int]:
    """Применяет таблицу возврата к плану: вес не выше прежнего, подходов не меньше одного."""
    if weight is not None and weight_pct:
        weight = min(weight, round_to_step(weight * (1 - weight_pct), step))
    return weight, max(1, round(sets * volume))


def is_light_day(sleep_quality: int | None, energy: int | None) -> bool:
    return any(v is not None and v <= R.LIGHT_DAY_LOW for v in (sleep_quality, energy))


def apply_light_day(weight: float | None, sets: int, step: float) -> tuple[float | None, int]:
    """«Лёгкий день»: тот же набор упражнений, вес −10% и на подход меньше (4.11)."""
    if weight is not None:
        weight = min(weight, round_to_step(weight * (1 - R.LIGHT_DAY_WEIGHT_PCT), step))
    return weight, max(1, sets - R.LIGHT_DAY_SETS_MINUS)
