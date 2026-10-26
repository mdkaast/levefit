"""Тесты движка решений: правила из data/programming_rules.md, раздел 4."""

import itertools
from datetime import date

import pytest

from app.engine import (
    RULES_VERSION,
    Context,
    ExerciseInput,
    PlanTarget,
    SessionSummary,
    SetResult,
    apply_light_day,
    apply_return,
    decide_exercise,
    decide_session,
    estimate_one_rep_max,
    is_light_day,
    return_factors,
    session_score,
    step_for,
)
from app.engine import rules as R


def sets(*results, weight=80.0, rir=None):
    """sets(8, 7, 6) → подходы с одним весом; rir применяется к последнему подходу."""
    out = [SetResult(weight, reps, None) for reps in results]
    if rir is not None and out:
        out[-1] = SetResult(weight, results[-1], rir)
    return tuple(out)


def item(*results, weight=80.0, plan=(80.0, 3, 8), rir=None, history=(), group="chest", **kw):
    return ExerciseInput(
        exercise_id=1,
        name="Жим лёжа",
        muscle_group=group,
        sets=sets(*results, weight=weight, rir=rir),
        plan=PlanTarget(*plan) if plan else None,
        history=history,
        **kw,
    )


def past(weight, *reps, day=date(2026, 10, 1)):
    return SessionSummary(
        day=day,
        top_weight_kg=weight,
        score=session_score(sets(*reps, weight=weight)),
        sets=sets(*reps, weight=weight),
    )


CTX = Context(experience="intermediate", goal="mass")


# ---------- двойная прогрессия ----------


def test_example_from_spec_keeps_weight_and_lifts_lagging_sets():
    """План 80 кг 3×8, факт 8/7/6 → вес не меняется, цель 8/8/7."""
    d = decide_exercise(item(8, 7, 6), CTX)
    assert d.action == "hold" and d.next_weight_kg == 80.0
    assert d.next_reps == (8, 8, 7) and d.next_sets == 3
    assert d.rule == "double_progression.hold"


def test_all_sets_at_top_increase_weight_and_reset_reps_to_range_bottom():
    d = decide_exercise(item(8, 8, 8), CTX)
    assert d.action == "increase" and d.next_weight_kg == 82.5
    assert d.next_reps == (6, 6, 6)  # возврат к нижней границе диапазона [6..8]
    assert d.rule == "double_progression.increase"


def test_increase_requires_all_planned_sets():
    d = decide_exercise(item(8, 8), CTX)  # выполнено 2 из 3
    assert d.action == "hold" and d.rule == "double_progression.hold_incomplete"
    assert d.next_sets == 3


def test_increase_needs_target_rir():
    ok = decide_exercise(item(8, 8, 8, rir=2), CTX)
    assert ok.action == "increase"
    close = decide_exercise(item(8, 8, 8, rir=1), CTX)  # запас меньше цели, но разрыв всего 1
    assert close.action == "hold" and close.rule == "double_progression.hold_rir"


def test_much_easier_than_target_gives_larger_step_capped_at_two_steps():
    d = decide_exercise(item(8, 8, 8, rir=5), CTX)  # запас 5 при цели 2 → разрыв 3
    assert d.action == "increase"
    assert 82.5 <= d.next_weight_kg <= 85.0
    assert d.next_weight_kg <= max(80 * 1.10, 80 + 2.5)


def test_too_hard_set_reduces_four_percent_per_extra_rep():
    d = decide_exercise(item(8, 8, 8, rir=0), CTX)  # запас 0 при цели 2 → разрыв 2
    assert d.action == "reduce" and d.rule == "rir.too_hard"
    assert d.next_weight_kg == 72.5  # 80 × (1 − 0.08) = 73,6 → ближайший шаг 72,5
    assert d.next_weight_kg < 80


def test_single_failed_session_is_ignored():
    d = decide_exercise(item(8, 7, 5), CTX)  # третий подход ниже 6
    assert d.action == "hold" and d.rule == "hold.first_miss" and d.next_weight_kg == 80.0


def test_second_failure_at_same_weight_resets():
    history = (past(80.0, 8, 6, 5),)
    d = decide_exercise(item(8, 6, 5, history=history), CTX)
    assert d.action == "reset" and d.rule == "stall.reset"
    assert d.next_weight_kg == 75.0  # 80 × 0,925 = 74 → ближайший шаг 75 (−6%)
    assert d.next_reps == (6, 6, 6)


def test_failure_after_different_weight_is_not_a_second_failure():
    history = (past(77.5, 8, 6, 5),)
    d = decide_exercise(item(8, 6, 5, history=history), CTX)
    assert d.rule == "hold.first_miss"


def test_weight_loss_goal_keeps_weight_instead_of_reset_for_non_beginners():
    history = (past(80.0, 8, 6, 5),)
    ctx = Context(experience="intermediate", goal="weight_loss")
    d = decide_exercise(item(8, 6, 5, history=history, plan=(80.0, 3, 12)), ctx)
    assert d.rule in ("deficit.hold", "double_progression.hold", "hold.first_miss")
    assert d.action == "hold" and d.next_weight_kg == 80.0
    ctx_new = Context(experience="beginner", goal="weight_loss")
    d2 = decide_exercise(item(8, 6, 5, history=history, plan=(80.0, 3, 8)), ctx_new)
    assert d2.action == "reset"


def test_beginner_lower_body_uses_five_kg_step():
    ctx = Context(experience="beginner", goal="mass")
    legs = ExerciseInput(
        1, "Приседания", "legs", sets(8, 8, 8, weight=60.0), PlanTarget(60.0, 3, 8)
    )
    assert step_for(legs, ctx) == 5.0
    assert decide_exercise(legs, ctx).next_weight_kg == 65.0
    assert step_for(legs, CTX) == 2.5


def test_beginner_target_rir_is_at_least_two():
    d = decide_exercise(item(8, 8, 8), Context(experience="beginner", goal="mass"))
    assert d.target_rir >= 2


def test_no_plan_uses_goal_default_and_does_not_jump():
    d = decide_exercise(item(8, 8, 8, plan=None), Context(experience="intermediate", goal="mass"))
    assert d.action == "hold"  # верх диапазона для «массы» — 10, до него ещё два повтора


def test_no_working_sets_changes_nothing():
    d = decide_exercise(ExerciseInput(1, "Жим", "chest", (SetResult(80.0, None, None),)), CTX)
    assert d.rule == "no_data.hold"


# ---------- упражнения с собственным весом ----------


def test_bodyweight_progression_adds_one_rep_when_all_sets_hit_top():
    bw = ExerciseInput(
        7,
        "Отжимания",
        "chest",
        tuple(SetResult(None, 12, None) for _ in range(3)),
        PlanTarget(None, 3, 12),
    )
    d = decide_exercise(bw, CTX)
    assert d.action == "increase" and d.next_weight_kg is None and d.next_reps == (13, 13, 13)
    lag = ExerciseInput(
        7,
        "Отжимания",
        "chest",
        (SetResult(None, 12, None), SetResult(None, 9, None)),
        PlanTarget(None, 2, 12),
    )
    dl = decide_exercise(lag, CTX)
    assert dl.action == "hold" and dl.next_reps == (12, 10)


# ---------- боль, самочувствие ----------


def test_pain_never_increases_and_lowers_weight():
    d = decide_exercise(item(8, 8, 8), Context(experience="intermediate", health_flag=True))
    assert d.action == "reduce" and d.rule == "pain.reduce"
    assert d.next_weight_kg < 80 and d.next_sets <= 3 and "pain" in d.flags


def test_low_readiness_blocks_increase_and_ignores_failures():
    ctx = Context(experience="intermediate", goal="mass", low_readiness=True)
    assert decide_exercise(item(8, 8, 8), ctx).action == "hold"
    d = decide_exercise(item(8, 6, 4, history=(past(80.0, 8, 6, 5),)), ctx)
    assert d.action == "hold" and d.rule == "readiness.hold" and d.next_weight_kg == 80.0


# ---------- разгрузка ----------


def test_reactive_deload_needs_two_signals():
    best = past(80.0, 8, 8, 8, day=date(2026, 9, 1))
    drops = (
        best,
        past(80.0, 6, 5, 5, day=date(2026, 9, 8)),
        past(80.0, 6, 5, 4, day=date(2026, 9, 15)),
    )
    one = decide_session((item(6, 5, 4, history=drops),), CTX)
    assert one.overall != "deload" and one.deload_signals == ("e1rm_drop",)

    tired = Context(
        experience="intermediate", goal="mass", low_readiness=True, recent_low_readiness=1
    )
    two = decide_session((item(6, 5, 4, history=drops),), tired)
    assert two.overall == "deload" and set(two.deload_signals) == {"e1rm_drop", "poor_recovery"}
    ex = two.exercises[0]
    assert ex.action == "deload" and ex.next_weight_kg == 80.0
    assert ex.next_sets == 2  # 3 × 0,55 → 2: подходов меньше
    assert ex.target_rir == 4  # RIR +2


def test_scheduled_deload():
    session = decide_session((item(8, 7, 6),), Context(experience="intermediate", deload_due=True))
    assert session.overall == "deload" and session.exercises[0].rule == "deload.scheduled"


def test_pain_has_priority_over_deload_for_the_exercise():
    ctx = Context(
        experience="intermediate", health_flag=True, low_readiness=True, recent_low_readiness=1
    )
    session = decide_session((item(8, 8, 8),), ctx)
    assert session.exercises[0].rule == "pain.reduce"
    assert session.overall == "reduce_weight"


# ---------- итог по тренировке ----------


def test_overall_decision_priority():
    inc = ExerciseInput(1, "Жим", "chest", sets(8, 8, 8), PlanTarget(80.0, 3, 8))
    hold = ExerciseInput(2, "Тяга", "back", sets(8, 7, 6, weight=60.0), PlanTarget(60.0, 3, 8))
    assert decide_session((hold,), CTX).overall == "keep_weight"
    assert decide_session((inc, hold), CTX).overall == "increase_weight"
    red = ExerciseInput(
        3, "Жим", "chest", sets(8, 8, 8, weight=80.0, rir=0), PlanTarget(80.0, 3, 8)
    )
    assert decide_session((inc, red), CTX).overall == "reduce_weight"
    assert decide_session((inc,), CTX).rules_version == RULES_VERSION


# ---------- возврат после перерыва, лёгкий день ----------


@pytest.mark.parametrize(
    ("days", "weight_pct", "volume"),
    [
        (0, 0.0, 1.0),
        (7, 0.0, 1.0),
        (10, 0.10, 0.75),
        (20, 0.20, 0.70),
        (45, 0.30, 0.50),
        (120, 0.40, 0.50),
    ],
)
def test_return_table(days, weight_pct, volume):
    assert return_factors(days, 30)[:2] == (weight_pct, volume)


def test_return_shifts_one_row_for_people_over_forty_and_flags_long_breaks():
    assert return_factors(10, 45)[:2] == (0.20, 0.70)
    assert return_factors(10, 30)[:2] == (0.10, 0.75)
    assert return_factors(300, 30)[2] is True
    assert return_factors(None, 30) == (0.0, 1.0, False)


def test_apply_return_lowers_weight_to_step_and_volume():
    assert apply_return(80.0, 4, 2.5, 0.10, 0.75) == (72.5, 3)
    assert apply_return(None, 3, 2.5, 0.10, 0.50) == (None, 2)
    assert apply_return(80.0, 1, 2.5, 0.0, 0.5) == (80.0, 1)  # хотя бы один подход


def test_light_day():
    assert is_light_day(2, 5) and is_light_day(5, 1) and not is_light_day(3, None)
    assert apply_light_day(80.0, 3, 2.5) == (72.5, 2)
    assert apply_light_day(60.0, 1, 2.5)[1] == 1


# ---------- расчётный максимум ----------


def test_one_rep_max_formula():
    assert estimate_one_rep_max(100, 5) == pytest.approx(116.67, abs=0.01)
    assert estimate_one_rep_max(None, 5) == 0
    assert session_score(sets(8, 7, 6)) == pytest.approx(80 * (1 + 8 / 30), abs=0.1)
    assert session_score((SetResult(None, 12, None), SetResult(None, 9, None))) == 12.0


# ---------- свойства: что движок не может сделать никогда ----------


def _cases():
    reps_options = [(8, 8, 8), (8, 7, 6), (8, 6, 4), (10, 10, 10), (5, 5, 5), (12, 12, 12, 12)]
    for reps, rir, health, light, exp, goal in itertools.product(
        reps_options,
        (None, 0, 1, 2, 4),
        (False, True),
        (False, True),
        ("beginner", "intermediate", "advanced"),
        ("mass", "strength", "weight_loss"),
    ):
        yield reps, rir, health, light, exp, goal


def test_engine_never_breaks_safety_invariants():
    checked = 0
    for reps, rir, health, light, exp, goal in _cases():
        ctx = Context(experience=exp, goal=goal, health_flag=health, low_readiness=light)
        exercise = item(*reps, plan=(80.0, len(reps), 8), rir=rir)
        d = decide_exercise(exercise, ctx)
        checked += 1
        assert d.next_sets >= 1 and all(r >= 1 for r in d.next_reps)
        if d.next_weight_kg is not None:
            assert d.next_weight_kg >= 0
            step = step_for(exercise, ctx)
            # рост веса за сессию не больше max(10%, шаг)
            assert d.next_weight_kg <= max(80 * (1 + R.MAX_GAIN_PCT), 80 + step) + 1e-6
            if health or light:
                assert d.next_weight_kg <= 80.0  # при боли и плохом самочувствии вес не растёт
        if health:
            assert d.action in ("reduce", "hold") and d.next_sets <= len(reps)
        if light:
            assert d.action != "increase"
    assert checked > 500


# ---------- дополнительные ветки и тексты ----------


def test_explicit_inventory_step_overrides_default():
    one = ExerciseInput(
        1, "Жим гантелей", "chest", sets(8, 8, 8, weight=20.0), PlanTarget(20.0, 3, 8), step_kg=1.25
    )
    assert step_for(one, CTX) == 1.25
    assert decide_exercise(one, CTX).next_weight_kg == 21.25


def test_pain_on_bodyweight_exercise_holds_volume():
    bw = ExerciseInput(
        7,
        "Отжимания",
        "chest",
        tuple(SetResult(None, 12, None) for _ in range(3)),
        PlanTarget(None, 3, 12),
    )
    d = decide_exercise(bw, Context(experience="intermediate", health_flag=True))
    assert d.action == "hold" and d.rule == "pain.hold" and d.next_sets <= 3


def test_range_top_is_kept_for_the_next_plan():
    up = decide_exercise(item(8, 8, 8), CTX)
    assert up.rep_max == 8 and up.next_reps == (6, 6, 6)
    bw = ExerciseInput(
        7,
        "Отжимания",
        "chest",
        tuple(SetResult(None, 12, None) for _ in range(3)),
        PlanTarget(None, 3, 12),
    )
    assert decide_exercise(bw, CTX).rep_max == 13


def test_kg_formatting():
    from app.engine import kg

    assert kg(82.5) == "82,5" and kg(80) == "80" and kg(None) == "свой вес"


def test_template_explanation_and_allowed_weights():
    from app.engine.explain import allowed_weights, describe, template_explanation

    plateau = ExerciseInput(
        1, "Жим лёжа", "chest", sets(8, 8, 8), PlanTarget(80.0, 3, 8), plateau=True
    )
    session = decide_session((plateau,), CTX)
    changes, rationale = template_explanation(session, health_flag=True)
    assert len(changes) == 1 and "врач" in rationale and "подряд" in rationale
    assert {80.0, 82.5, 2.5} <= allowed_weights(session, {1: 1.25}) | {2.5}
    assert 1.25 in allowed_weights(session, {1: 1.25})
    assert describe(session)[0]["rule"] == "double_progression.increase"
    for overall in ("increase_weight", "keep_weight", "reduce_weight", "deload"):
        fake = session.__class__(session.rules_version, overall, session.exercises)
        assert template_explanation(fake, health_flag=False)[1]
