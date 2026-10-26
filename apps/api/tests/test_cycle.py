from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models import AiAdjustment, SkippedSession, WorkoutSet
from tests.test_ai_adjust import FakeLLM, explanation, plan_for, setup_workout


def add_set(client, headers, wid, exercise_id, client_id=None, reps=8):
    return client.post(
        f"/workouts/{wid}/sets",
        json={"exercise_id": exercise_id, "weight_kg": 80, "reps": reps, "client_id": client_id},
        headers=headers,
    )


# ---------- идемпотентная запись подхода (офлайн-очередь) ----------


def test_set_with_same_client_id_is_not_duplicated(client, auth_headers, exercises):
    headers = auth_headers()
    bench = exercises["strength"]
    wid = client.post("/workouts", json={}, headers=headers).json()["id"]
    first = add_set(client, headers, wid, bench, "11111111-aaaa-bbbb-cccc-000000000001")
    again = add_set(client, headers, wid, bench, "11111111-aaaa-bbbb-cccc-000000000001")
    other = add_set(client, headers, wid, bench, "11111111-aaaa-bbbb-cccc-000000000002")
    assert first.status_code == again.status_code == other.status_code == 201
    assert first.json()["id"] == again.json()["id"] != other.json()["id"]
    assert [first.json()["set_no"], other.json()["set_no"]] == [1, 2]
    with client.session_factory() as s:
        assert s.query(WorkoutSet).count() == 2


def test_sets_without_client_id_still_work(client, auth_headers, exercises):
    headers = auth_headers()
    bench = exercises["strength"]
    wid = client.post("/workouts", json={}, headers=headers).json()["id"]
    assert add_set(client, headers, wid, bench).status_code == 201
    assert add_set(client, headers, wid, bench).status_code == 201


def test_client_id_must_look_like_an_id(client, auth_headers, exercises):
    headers = auth_headers()
    wid = client.post("/workouts", json={}, headers=headers).json()["id"]
    assert add_set(client, headers, wid, exercises["strength"], "x").status_code == 422


# ---------- оценка упражнения ----------


def test_rating_is_saved_and_listed_and_overwritten(client, auth_headers, exercises):
    headers = auth_headers()
    bench = exercises["strength"]
    wid = client.post("/workouts", json={}, headers=headers).json()["id"]
    url = f"/workouts/{wid}/ratings/{bench}"
    assert client.put(url, json={"rating": "hard"}, headers=headers).json() == {
        "exercise_id": bench,
        "rating": "hard",
        "pain": False,
    }
    client.put(url, json={"rating": "easy", "pain": True}, headers=headers)
    assert client.get(f"/workouts/{wid}/ratings", headers=headers).json() == [
        {"exercise_id": bench, "rating": "easy", "pain": True}
    ]
    assert client.put(url, json={"rating": "meh"}, headers=headers).status_code == 422
    assert (
        client.put(
            f"/workouts/{wid}/ratings/999", json={"rating": "easy"}, headers=headers
        ).status_code
        == 404
    )


def test_rating_is_private_and_closed_after_decision(client, auth_headers, exercises, use_llm):
    owner = auth_headers({"id": 1, "first_name": "A"})
    other = auth_headers({"id": 2, "first_name": "B"})
    bench = exercises["strength"]
    wid = setup_workout(client, owner, bench)
    assert (
        client.put(
            f"/workouts/{wid}/ratings/{bench}", json={"rating": "easy"}, headers=other
        ).status_code
        == 404
    )
    use_llm(FakeLLM(explanation()))
    client.post(f"/workouts/{wid}/adjust", json=plan_for(bench), headers=owner)
    assert (
        client.put(
            f"/workouts/{wid}/ratings/{bench}", json={"rating": "easy"}, headers=owner
        ).status_code
        == 409
    )


def test_hard_rating_blocks_weight_increase(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    full = ((80, 8), (80, 8), (80, 8))
    wid = setup_workout(client, headers, bench, sets=full, rir=None)
    client.put(f"/workouts/{wid}/ratings/{bench}", json={"rating": "hard"}, headers=headers)
    use_llm(FakeLLM(explanation()))
    body = client.post(f"/workouts/{wid}/adjust", json=plan_for(bench), headers=headers).json()
    assert body["decision"] == "keep_weight" and body["engine"][0]["rule"] == "rating.hold"
    assert body["next_workout"][0]["target_weight_kg"] == 80.0


def test_without_rating_all_top_sets_raise_weight_and_easy_allows_it(
    client, auth_headers, exercises, use_llm
):
    headers = auth_headers()
    bench = exercises["strength"]
    full = ((80, 8), (80, 8), (80, 8))
    plain = setup_workout(client, headers, bench, sets=full, rir=None)
    use_llm(FakeLLM(explanation("Все подходы выполнены, вес повышаем на 2,5 кг.")))
    assert (
        client.post(f"/workouts/{plain}/adjust", json=plan_for(bench), headers=headers).json()[
            "decision"
        ]
        == "increase_weight"
    )

    easy = setup_workout(client, headers, bench, sets=full, rir=1)  # запас 1 при цели 2
    client.put(f"/workouts/{easy}/ratings/{bench}", json={"rating": "easy"}, headers=headers)
    body = client.post(f"/workouts/{easy}/adjust", json=plan_for(bench), headers=headers).json()
    assert body["decision"] == "increase_weight"


def test_pain_in_rating_or_before_workout_counts_as_health_flag(
    client, auth_headers, exercises, use_llm
):
    headers = auth_headers()
    bench = exercises["strength"]
    full = ((80, 8), (80, 8), (80, 8))
    rated = setup_workout(client, headers, bench, sets=full, rir=None)
    client.put(
        f"/workouts/{rated}/ratings/{bench}",
        json={"rating": "normal", "pain": True},
        headers=headers,
    )
    use_llm(FakeLLM(explanation("Нагрузка не растёт. При боли обратитесь к врачу.")))
    body = client.post(f"/workouts/{rated}/adjust", json=plan_for(bench), headers=headers).json()
    assert body["health_flag"] is True and body["decision"] == "reduce_weight"

    before = setup_workout(client, headers, bench, sets=full, rir=None, pain=True)
    body2 = client.post(f"/workouts/{before}/adjust", json=plan_for(bench), headers=headers).json()
    assert body2["health_flag"] is True and body2["next_workout"][0]["target_weight_kg"] < 80


# ---------- пропуски ----------


def test_skip_is_recorded_once_per_day_and_can_be_undone(client, auth_headers):
    headers = auth_headers()
    assert client.post("/skips", json={"kind": "move"}, headers=headers).status_code == 201
    again = client.post("/skips", json={"kind": "rest"}, headers=headers)
    assert again.status_code == 201 and again.json()["kind"] == "rest"
    with client.session_factory() as s:
        assert s.query(SkippedSession).count() == 1
    assert client.get("/plan", headers=headers).json()["skipped_today"] == "rest"
    assert client.delete("/skips/today", headers=headers).status_code == 204
    assert client.get("/plan", headers=headers).json()["skipped_today"] is None
    assert client.post("/skips", json={"kind": "later"}, headers=headers).status_code == 422
    assert client.post("/skips", json={"kind": "move"}).status_code == 401


def test_skip_does_not_take_away_xp_or_streak(client, auth_headers, exercises):
    headers = auth_headers()
    client.post("/characters", json={"name": "Игрок"}, headers=headers)
    before = client.get("/me", headers=headers).json()
    client.post("/skips", json={"kind": "move"}, headers=headers)
    after = client.get("/me", headers=headers).json()
    assert after["character"]["xp"] == before["character"]["xp"]
    assert after["streak"] == before["streak"]


def test_two_skips_plus_poor_recovery_trigger_deload(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    day = (datetime.now(UTC) - timedelta(days=1)).date()
    with client.session_factory() as s:
        user_id = client.get("/me", headers=headers).json()["user"]["id"]
        s.add_all(
            [
                SkippedSession(user_id=user_id, day=day, kind="move"),
                SkippedSession(user_id=user_id, day=day - timedelta(days=2), kind="rest"),
            ]
        )
        s.commit()
    wid = setup_workout(
        client,
        headers,
        bench,
        sets=((80, 8),) * 3,
        rir=None,
        sleep_quality=2,
        date=datetime.now(UTC).date().isoformat(),
    )
    # сигналы: два пропуска и плохое самочувствие сегодня → разгрузка
    use_llm(FakeLLM(explanation()))
    body = client.post(f"/workouts/{wid}/adjust", json=plan_for(bench), headers=headers).json()
    assert body["decision"] != "increase_weight"
    with client.session_factory() as s:
        saved = s.scalar(select(AiAdjustment))
        assert saved.engine_decisions[0]["rule"] in ("deload.reactive", "readiness.hold")


# ---------- правка решения пользователем ----------


def test_user_can_override_the_weight_and_it_is_journaled(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    wid = setup_workout(client, headers, bench, sets=((80, 8),) * 3, rir=2)
    use_llm(FakeLLM(explanation()))
    client.post(f"/workouts/{wid}/adjust", json=plan_for(bench), headers=headers)  # → 82,5
    url = f"/workouts/{wid}/adjust/exercise/{bench}"
    body = client.patch(
        url, json={"weight_kg": 80, "reason": "Плечо ещё не готово"}, headers=headers
    )
    assert body.status_code == 200 and body.json()["next_workout"][0]["target_weight_kg"] == 80.0
    assert client.get("/plan", headers=headers).json()["items"][0]["target_weight_kg"] == 80.0
    with client.session_factory() as s:
        saved = s.scalar(select(AiAdjustment))
        assert saved.overrides[0]["from_weight_kg"] == 82.5
        assert saved.overrides[0]["to_weight_kg"] == 80.0 and saved.overrides[0]["reason"]
        assert saved.engine_decisions[0]["next_weight_kg"] == 82.5  # решение движка не затёрто


def test_override_validation_and_ownership(client, auth_headers, exercises, use_llm):
    owner = auth_headers({"id": 1, "first_name": "A"})
    other = auth_headers({"id": 2, "first_name": "B"})
    bench = exercises["strength"]
    wid = setup_workout(client, owner, bench)
    url = f"/workouts/{wid}/adjust/exercise/{bench}"
    assert (
        client.patch(url, json={"weight_kg": 70}, headers=owner).status_code == 404
    )  # решения нет
    use_llm(FakeLLM(explanation()))
    client.post(f"/workouts/{wid}/adjust", json=plan_for(bench), headers=owner)
    assert client.patch(url, json={"weight_kg": 70}, headers=other).status_code == 404
    assert client.patch(url, json={"weight_kg": -1}, headers=owner).status_code == 422
    assert client.patch(url, json={"weight_kg": 5000}, headers=owner).status_code == 422
    assert (
        client.patch(
            f"/workouts/{wid}/adjust/exercise/999", json={"weight_kg": 70}, headers=owner
        ).status_code
        == 404
    )
    assert client.patch(url, json={"weight_kg": 70}).status_code == 401


def test_plan_lists_the_reasons_of_the_last_decision(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    wid = setup_workout(client, headers, bench, sets=((80, 8),) * 3, rir=2)
    use_llm(FakeLLM(explanation()))
    client.post(f"/workouts/{wid}/adjust", json=plan_for(bench), headers=headers)
    plan = client.get("/plan", headers=headers).json()
    assert plan["decisions"] and "82,5" in plan["decisions"][0]


def test_last_session_returns_the_previous_attempt(client, auth_headers, exercises):
    headers = auth_headers()
    bench = exercises["strength"]
    assert client.get(f"/exercises/{bench}/last", headers=headers).json() is None
    setup_workout(client, headers, bench, sets=((77.5, 8), (77.5, 8), (77.5, 7)), rir=None)
    last = client.get(f"/exercises/{bench}/last", headers=headers).json()
    assert last["top_weight_kg"] == 77.5
    assert [s["reps"] for s in last["sets"]] == [8, 8, 7]
    assert client.get("/exercises/999/last", headers=headers).status_code == 404
    assert client.get(f"/exercises/{bench}/last").status_code == 401
