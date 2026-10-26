"""Направления, планировщик недели, акценты и предпросмотр (фаза 3)."""

from datetime import date, timedelta
from itertools import product

import pytest

from app import week
from app.content import directions
from app.content.seed import seed_catalog

MONDAY = date(2026, 10, 26)  # понедельник
WEDNESDAY = MONDAY + timedelta(days=2)


@pytest.fixture
def planner(client, auth_headers, monkeypatch):
    """Пользователь со средним уровнем и залом; «сегодня» — среда, неделя идёт с 26 октября."""
    with client.session_factory() as session:
        seed_catalog(session)
    state = {"today": WEDNESDAY}
    monkeypatch.setattr(week, "today", lambda: state["today"])
    headers = auth_headers()
    client.post(
        "/characters",
        json={
            "name": "Игрок",
            "goal": "mass",
            "experience": "intermediate",
            "workouts_per_week": 4,
            "equipment": "gym",
        },
        headers=headers,
    )
    client.headers_ = headers
    client.state = state
    return client


def put_directions(client, items):
    body = {"items": [{"direction": d, "days": n} for d, n in items]}
    return client.put("/me/directions", json=body, headers=client.headers_)


def current_week(client, offset=0):
    r = client.get(f"/week?offset={offset}", headers=client.headers_)
    assert r.status_code == 200, r.text
    return r.json()


# ---------- данные направлений ----------


def test_every_non_strength_direction_has_six_unverified_sessions():
    for key in ("running", "yoga", "crossfit", "functional"):
        sessions = directions.SESSION_TEMPLATES[key]
        assert len(sessions) == 6
        assert all(not s["verified"] for s in sessions)
        assert {s["quality"] for s in sessions} <= set(directions.QUALITIES[key])


def test_accent_selection_rules():
    assert directions.valid_accent("gym", ["chest", "lats"])
    assert not directions.valid_accent("gym", ["chest", "lats", "abs"])  # не больше двух
    assert not directions.valid_accent("gym", ["chest", "chest"])
    assert not directions.valid_accent("gym", ["flexibility"])
    assert directions.valid_accent("yoga", ["flexibility", "posture"])
    assert not directions.valid_accent("universal", ["chest"])


# ---------- расстановка по дням ----------


def _fake(direction, number, tags=()):
    return {"direction": direction, "key": f"{direction}:{number}", "tags": list(tags)}


def test_heavy_legs_and_intervals_are_never_adjacent():
    sessions = [
        _fake("gym", 0, ["heavy_legs"]),
        _fake("gym", 1, ["heavy_legs"]),
        _fake("running", 0, ["intervals"]),
        _fake("running", 1),
    ]
    slots, found = week.schedule(sessions)
    assert found == []
    days = [i for i, s in enumerate(slots) if s]
    assert len(days) == 4
    for first, second in zip(slots, slots[1:], strict=False):
        if first and second:
            assert not week._conflict(first, second)


def test_order_inside_a_direction_is_kept():
    sessions = [_fake("gym", i) for i in range(3)]
    slots, _ = week.schedule(sessions)
    order = [s["key"] for s in slots if s]
    assert order == ["gym:0", "gym:1", "gym:2"]


def test_three_sessions_get_the_classic_monday_wednesday_friday():
    slots, _ = week.schedule([_fake("gym", i) for i in range(3)])
    assert [i for i, s in enumerate(slots) if s] == [0, 2, 4]


def test_scheduler_never_breaks_rules_for_feasible_combinations():
    """Любая смесь сессий из 5 дней: либо без нарушений, либо нарушение действительно неизбежно."""
    pool = {
        "L": ["heavy_legs"],
        "I": ["intervals"],
        "E": [],
    }
    for combo in product("LIE", repeat=5):
        sessions = [_fake("d%d" % i, 0, pool[c]) for i, c in enumerate(combo)]
        slots, found = week.schedule(sessions)
        assert sum(1 for s in slots if s) == 5
        taxing = sum(1 for c in combo if c in "LI")
        if taxing <= 3:  # три тяжёлых из 7 дней всегда можно развести пустыми днями или лёгкими
            assert found == [], combo


def test_no_more_than_three_training_days_in_a_row():
    slots, found = week.schedule([_fake("d%d" % i, 0) for i in range(5)])
    assert found == []
    run = best = 0
    for session in slots:
        run = run + 1 if session else 0
        best = max(best, run)
    assert best <= week.MAX_RUN


# ---------- API направлений ----------


def test_default_state_uses_gym_and_does_not_follow_the_week(planner):
    state = planner.get("/directions", headers=planner.headers_).json()
    assert state["mine"] == [{"direction": "gym", "days": 4}]
    assert state["saved"] is False and state["follows_week"] is False
    assert state["max_days"] == 5
    assert {d["key"] for d in state["catalog"]} == set(directions.DIRECTIONS)


def test_save_directions_and_validation(planner):
    response = put_directions(planner, [("gym", 3), ("running", 2)])
    assert response.status_code == 200
    state = response.json()
    assert state["saved"] and state["total_days"] == 5
    assert put_directions(planner, [("karate", 2)]).status_code == 422
    assert put_directions(planner, [("gym", 3), ("gym", 2)]).status_code == 422
    assert put_directions(planner, [("gym", 9)]).status_code == 422
    assert put_directions(planner, [("gym", 0)]).status_code == 422


def test_week_has_seven_days_and_the_right_session_count(planner):
    put_directions(planner, [("gym", 3), ("running", 2)])
    data = current_week(planner)
    assert len(data["days"]) == 7 and data["follows_week"] is True
    sessions = [d["session"] for d in data["days"] if d["session"]]
    assert len(sessions) == 5
    assert {s["direction"] for s in sessions} == {"gym", "running"}
    strength = [s for s in sessions if s["kind"] == "strength"]
    assert strength and all(s["exercises"] for s in strength)
    run = [s for s in sessions if s["kind"] == "session"]
    assert all(s["blocks"] and s["verified"] is False for s in run)
    assert data["violations"] == []


def test_overload_is_reported_and_capped(planner):
    put_directions(planner, [("gym", 4), ("running", 3)])
    data = current_week(planner)
    assert sum(1 for d in data["days"] if d["session"]) == 5
    assert any(w.startswith("overload") for w in data["warnings"])


# ---------- акцент: с понедельника, текущая неделя не меняется ----------


def test_accent_applies_from_next_monday_and_keeps_current_week(planner):
    put_directions(planner, [("gym", 3)])
    before = current_week(planner)
    response = planner.put(
        "/me/accent", json={"direction": "gym", "selection": ["biceps"]}, headers=planner.headers_
    )
    assert response.status_code == 200
    assert response.json()["effective_from"] == (MONDAY + timedelta(days=7)).isoformat()
    assert current_week(planner) == before  # текущая неделя не изменилась
    assert not any(
        e["accent"] for d in before["days"] if d["session"] for e in d["session"]["exercises"]
    )
    upcoming = current_week(planner, offset=1)
    accented = [
        e
        for d in upcoming["days"]
        if d["session"]
        for e in d["session"]["exercises"]
        if e["accent"] == "biceps"
    ]
    assert len(accented) == 1 and accented[0]["sets"] == directions.ACCENT_EXTRA_SETS
    # когда наступает понедельник, неделя строится с акцентом и замораживается
    planner.state["today"] = MONDAY + timedelta(days=7)
    new_week = current_week(planner)
    assert any(
        e["accent"] == "biceps"
        for d in new_week["days"]
        if d["session"]
        for e in d["session"]["exercises"]
    )


def test_accent_adds_two_sets_to_the_chosen_group(planner):
    put_directions(planner, [("gym", 3)])
    base = {v["group"]: v["sets"] for v in current_week(planner, offset=1)["volume"]}
    planner.put(
        "/me/accent", json={"direction": "gym", "selection": ["triceps"]}, headers=planner.headers_
    )
    after = {v["group"]: v["sets"] for v in current_week(planner, offset=1)["volume"]}
    assert after["triceps"] > base.get("triceps", 0)
    assert round(after["triceps"] - base.get("triceps", 0), 1) >= directions.ACCENT_EXTRA_SETS


def test_accent_validation(planner):
    put_directions(planner, [("gym", 3)])
    for selection in (["chest", "abs", "lats"], ["nope"], ["chest", "chest"]):
        r = planner.put(
            "/me/accent",
            json={"direction": "gym", "selection": selection},
            headers=planner.headers_,
        )
        assert r.status_code == 422, selection
    r = planner.put(
        "/me/accent", json={"direction": "universal", "selection": []}, headers=planner.headers_
    )
    assert r.status_code == 422


def test_accent_is_capped_by_weekly_volume(planner, monkeypatch):
    put_directions(planner, [("gym", 3)])
    monkeypatch.setattr(week, "WEEKLY_SETS_CAP", 1)
    planner.put(
        "/me/accent", json={"direction": "gym", "selection": ["chest"]}, headers=planner.headers_
    )
    data = current_week(planner, offset=1)
    assert "accent_capped:chest" in data["warnings"]
    assert not any(
        e["accent"] for d in data["days"] if d["session"] for e in d["session"]["exercises"]
    )


def test_every_accent_group_finds_an_exercise_for_every_inventory(planner):
    """Акцент не должен молча пропадать из-за инвентаря: в каждом профиле есть упражнение."""
    from app import programs

    with planner.session_factory() as db:
        catalog = programs.load_catalog(db)
    from app.content import resolver

    for key, spec in directions.ACCENT_ACCESSORY.items():
        for inventory in resolver.INVENTORIES:
            slot = {**spec, "role": "accessory", "sets": [2, 2], "progression": "double"}
            found = resolver.resolve_slot(
                slot, catalog, resolver.inventory_items(inventory), "beginner"
            )
            assert found.slug, (key, inventory)


# ---------- предпросмотр ----------


def test_preview_shows_changes_without_saving(planner):
    put_directions(planner, [("gym", 3)])
    saved_before = planner.get("/directions", headers=planner.headers_).json()
    result = planner.post(
        "/week/preview",
        json={"accent": {"direction": "gym", "selection": ["abs"]}},
        headers=planner.headers_,
    ).json()
    assert result["effective_from"] == (MONDAY + timedelta(days=7)).isoformat()
    assert result["current_week_unchanged"] is True
    assert result["changes"], "акцент должен что-то менять в следующей неделе"
    assert any("+ " in line for change in result["changes"] for line in change["details"])
    assert planner.get("/directions", headers=planner.headers_).json() == saved_before
    # без изменений предпросмотр пуст
    same = planner.post("/week/preview", json={}, headers=planner.headers_).json()
    assert same["changes"] == [] and same["volume"] == []


def test_preview_for_new_directions(planner):
    put_directions(planner, [("gym", 3)])
    result = planner.post(
        "/week/preview",
        json={"directions": [{"direction": "gym", "days": 3}, {"direction": "yoga", "days": 2}]},
        headers=planner.headers_,
    ).json()
    kinds = {c["kind"] for c in result["changes"]}
    assert "added" in kinds
    assert (
        planner.post(
            "/week/preview",
            json={"directions": [{"direction": "x", "days": 1}]},
            headers=planner.headers_,
        ).status_code
        == 422
    )


def test_changing_directions_does_not_touch_the_current_week(planner):
    put_directions(planner, [("gym", 3)])
    before = current_week(planner)
    put_directions(planner, [("gym", 2), ("yoga", 2)])
    assert current_week(planner) == before
    planner.state["today"] = MONDAY + timedelta(days=7)
    nxt = current_week(planner)
    assert {d["session"]["direction"] for d in nxt["days"] if d["session"]} == {"gym", "yoga"}


# ---------- «Сегодня» по неделе ----------


def test_plan_follows_the_week_after_saving_directions(planner):
    before = planner.get("/plan", headers=planner.headers_).json()
    assert before["source"] == "starter" and before["session"] is None
    put_directions(planner, [("gym", 3)])
    plan = planner.get("/plan", headers=planner.headers_).json()
    assert plan["source"] == "week" and plan["session"]["direction"] == "gym"
    assert plan["items"] and all(i["sets"] >= 1 and i["reps"] >= 1 for i in plan["items"])


def test_plan_on_a_non_strength_day_gives_blocks_and_no_exercises(planner):
    put_directions(planner, [("yoga", 3)])
    plan = planner.get("/plan", headers=planner.headers_).json()
    assert plan["source"] == "week" and plan["items"] == []
    assert plan["session"]["kind"] == "session" and plan["session"]["blocks"]


def test_silhouette_is_saved_in_profile(planner):
    r = planner.patch("/me/character", json={"silhouette": "female"}, headers=planner.headers_)
    assert r.status_code == 200 and r.json()["silhouette"] == "female"
    assert (
        planner.patch(
            "/me/character", json={"silhouette": "robot"}, headers=planner.headers_
        ).status_code
        == 422
    )
    # прежний вызов с одними мышцами по-прежнему работает
    r = planner.patch("/me/character", json={"target_muscles": ["chest"]}, headers=planner.headers_)
    assert r.status_code == 200 and r.json()["target_muscles"] == ["chest"]
    assert r.json()["silhouette"] == "female"


def test_legacy_target_muscles_become_the_gym_accent(planner):
    planner.patch("/me/character", json={"target_muscles": ["arms"]}, headers=planner.headers_)
    state = planner.get("/directions", headers=planner.headers_).json()
    assert state["accents"]["gym"]["current"] == ["biceps", "triceps"]
