import pytest
from sqlalchemy import select

from app.engine import estimate_one_rep_max
from app.models import AiAdjustment
from app.progress import is_plateau, sessions_since_best
from tests.test_ai_adjust import FakeLLM, explanation, plan_for


def finished_workout(client, headers, exercise_id, day, sets=((80, 8),), rir=1, **extra):
    created = client.post("/workouts", json={"date": day, **extra}, headers=headers)
    assert created.status_code == 201, created.text
    wid = created.json()["id"]
    for weight, reps in sets:
        r = client.post(
            f"/workouts/{wid}/sets",
            json={"exercise_id": exercise_id, "weight_kg": weight, "reps": reps, "rir": rir},
            headers=headers,
        )
        assert r.status_code == 201, r.text
    assert client.post(f"/workouts/{wid}/finish", headers=headers).status_code == 200
    return wid


def test_estimate_one_rep_max():
    assert estimate_one_rep_max(100, 5) == pytest.approx(116.67, abs=0.01)
    assert estimate_one_rep_max(None, 10) == 0
    assert estimate_one_rep_max(80, None) == 0


def test_plateau_detection_rules():
    assert sessions_since_best([]) == 0
    assert sessions_since_best([100, 105, 110]) == 0
    assert sessions_since_best([100, 110, 110, 109, 110.5]) == 0  # в пределах допуска 1%
    assert sessions_since_best([100, 110, 105, 104, 103]) == 3
    assert is_plateau([100, 110, 105, 104, 103])
    assert not is_plateau([100, 110, 105, 104])  # мало тренировок без роста
    assert not is_plateau([110, 105, 104])  # меньше минимального числа тренировок
    assert not is_plateau([0, 0, 0, 0, 0])


def test_progress_endpoint_marks_plateau(client, auth_headers, exercises):
    headers = auth_headers()
    bench = exercises["strength"]
    days = ["2026-10-01", "2026-10-04", "2026-10-07", "2026-10-10", "2026-10-13"]
    for day, reps in zip(days, (8, 8, 7, 6, 6), strict=True):
        finished_workout(client, headers, bench, day, sets=((80, reps),))
    data = client.get("/progress/exercises", headers=headers).json()
    assert len(data) == 1 and data[0]["name"] == "Жим лёжа"
    assert data[0]["plateau"] is True and data[0]["sessions_without_gain"] == 3
    assert [p["date"] for p in data[0]["points"]] == days
    assert data[0]["points"][0]["top_weight_kg"] == 80.0
    assert client.get("/progress/exercises").status_code == 401


def test_progress_without_plateau_when_growing(client, auth_headers, exercises):
    headers = auth_headers()
    bench = exercises["strength"]
    for i, day in enumerate(["2026-10-01", "2026-10-04", "2026-10-07", "2026-10-10"]):
        finished_workout(client, headers, bench, day, sets=((80 + 2.5 * i, 8),))
    data = client.get("/progress/exercises", headers=headers).json()
    assert data[0]["plateau"] is False and data[0]["sessions_without_gain"] == 0


def test_context_contains_history_plateau_and_past_decisions(
    client, auth_headers, exercises, use_llm
):
    headers = auth_headers()
    bench = exercises["strength"]
    llm = use_llm(FakeLLM(explanation()))
    days = ["2026-10-01", "2026-10-04", "2026-10-07", "2026-10-10"]
    for day in days[:-1]:
        wid = finished_workout(client, headers, bench, day, sets=((80, 6),))
    client.post(f"/workouts/{wid}/adjust", headers=headers)
    client.post(f"/workouts/{wid}/adjust/feedback", json={"rating": "too_hard"}, headers=headers)
    first = finished_workout(client, headers, bench, "2026-10-01", sets=((85, 8),))  # лучший
    assert first
    last = finished_workout(client, headers, bench, days[-1], sets=((80, 6),))
    assert client.post(f"/workouts/{last}/adjust", headers=headers).status_code == 200

    context = llm.snapshots[-1]["context"]
    history = context["exercises"][0]["history"]
    assert history["sessions_total"] >= 4
    assert history["plateau"] is True
    assert history["recent_sessions"][-1]["sets"] == [{"weight_kg": 80.0, "reps": 6, "rir": 1}]
    assert context["past_decisions"] == [
        {"date": "2026-10-07", "decision": "reduce_weight", "user_rating": "too_hard"}
    ]
    assert "plateau" in llm.snapshots[-1]["engine_decisions"][0]["flags"]


def test_reactive_deload_from_history_and_poor_recovery(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    best = ((80, 8), (80, 8), (80, 8))
    drop = ((80, 5), (80, 5), (80, 5))
    finished_workout(client, headers, bench, "2026-10-01", sets=best, rir=2)
    finished_workout(client, headers, bench, "2026-10-04", sets=drop, rir=2, sleep_quality=2)
    last = finished_workout(client, headers, bench, "2026-10-07", sets=drop, rir=2, sleep_quality=2)
    llm = use_llm(FakeLLM(explanation()))
    body = client.post(f"/workouts/{last}/adjust", json=plan_for(bench), headers=headers).json()
    assert body["decision"] == "deload" and body["engine"][0]["rule"] == "deload.reactive"
    item = body["next_workout"][0]
    assert item["target_weight_kg"] == 80.0 and item["sets"] == 2  # вес тот же, подходов меньше
    assert llm.snapshots[0]["deload_signals"] == ["e1rm_drop", "poor_recovery"]


def test_low_readiness_blocks_weight_growth(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    full = ((80, 8), (80, 8), (80, 8))
    tired = finished_workout(
        client, headers, bench, "2026-10-01", sets=full, rir=2, sleep_quality=2, energy=4
    )
    llm = use_llm(FakeLLM(explanation()))
    body = client.post(f"/workouts/{tired}/adjust", json=plan_for(bench), headers=headers).json()
    assert body["decision"] == "keep_weight" and body["engine"][0]["rule"] == "readiness.hold"
    assert body["next_workout"][0]["target_weight_kg"] == 80.0
    context = llm.snapshots[0]["context"]
    assert context["low_readiness"] is True
    assert context["checkin"] == {"sleep_quality": 2, "energy": 4}

    fresh = finished_workout(
        client, headers, bench, "2026-10-02", sets=full, rir=2, sleep_quality=4, energy=5
    )
    use_llm(FakeLLM(explanation("Все подходы выполнены, вес повышаем на 2,5 кг.")))
    ok = client.post(f"/workouts/{fresh}/adjust", json=plan_for(bench), headers=headers).json()
    assert ok["decision"] == "increase_weight" and ok["next_workout"][0]["target_weight_kg"] == 82.5


def test_checkin_validation(client, auth_headers):
    headers = auth_headers()
    assert client.post("/workouts", json={"energy": 6}, headers=headers).status_code == 422
    assert client.post("/workouts", json={"sleep_quality": 0}, headers=headers).status_code == 422
    assert client.post("/workouts", json={"energy": 3}, headers=headers).status_code == 201


def test_starter_plan_follows_profile(client, auth_headers, exercises):
    headers = auth_headers()
    assert client.get("/plan", headers=headers).json()["items"] == []  # профиля ещё нет
    body = {
        "name": "Игрок",
        "goal": "mass",
        "experience": "intermediate",
        "equipment": "gym",
        "target_muscles": ["chest", "legs"],
    }
    assert client.post("/characters", json=body, headers=headers).status_code == 201
    plan = client.get("/plan", headers=headers).json()
    assert plan["source"] == "starter" and plan["workout_id"] is None
    assert plan["items"] == [
        {
            "exercise_id": exercises["strength"],
            "name": "Жим лёжа",
            "target_weight_kg": None,
            "sets": 3,
            "reps": 8,
            "rep_targets": None,
        }
    ]


def test_starter_plan_uses_bodyweight_exercises_without_equipment(client, auth_headers, exercises):
    headers = auth_headers()
    body = {"name": "Игрок", "goal": "strength", "equipment": "none", "target_muscles": ["chest"]}
    assert client.post("/characters", json=body, headers=headers).status_code == 201
    assert client.get("/plan", headers=headers).json()["items"] == []  # «Жим лёжа» нужен зал


def test_tokens_are_saved_for_unit_economics(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    llm = FakeLLM(explanation())
    llm.last_usage = (1200, 340)
    use_llm(llm)
    wid = finished_workout(client, headers, bench, "2026-10-01", sets=((80, 8),))
    assert client.post(f"/workouts/{wid}/adjust", headers=headers).status_code == 200
    with client.session_factory() as s:
        saved = s.scalar(select(AiAdjustment))
        assert (saved.input_tokens, saved.output_tokens) == (1200, 340)
