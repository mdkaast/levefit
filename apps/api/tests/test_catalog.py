"""Каталог упражнений, шаблоны программ и матрица выбора (фаза 2)."""

import json
from datetime import UTC, datetime, timedelta
from itertools import product

import pytest
from sqlalchemy import func, select

from app.content import matrix, resolver
from app.content.seed import CONTENT, seed_catalog
from app.content.templates_data import LADDERS, TEMPLATES
from app.models import Exercise, ExerciseMuscle, ProgramTemplate, TemplateMatrix

CATALOG = {
    e["slug"]: e for e in json.loads((CONTENT / "exercises.json").read_text(encoding="utf-8"))
}
BY_ID = {t["id"]: t for t in TEMPLATES}
LEVELS = ("beginner", "intermediate", "advanced")


# ---------- целостность данных (без БД) ----------


def test_catalog_has_all_374_unique_exercises():
    source = json.loads(
        (CONTENT.parents[3] / "data" / "exercises.json").read_text(encoding="utf-8")
    )
    assert len(CATALOG) == len(source) == 374
    assert all(1 <= len(e["name_ru"]) <= 120 and e["name_en"] for e in CATALOG.values())
    assert {e["category"] for e in CATALOG.values()} == {"strength", "cardio", "mobility"}


def test_every_strength_exercise_has_primary_muscles_and_a_group():
    for slug, e in CATALOG.items():
        if e["category"] == "strength":
            assert any(m["role"] == "primary" for m in e["muscles"]), slug
            assert e["ui_groups"] and e["legacy_group"], slug


def test_references_between_exercises_are_valid():
    for slug, e in CATALOG.items():
        assert e["variant_of"] is None or e["variant_of"] in CATALOG, slug
        for slugs in e["subs"].values():
            assert all(s in CATALOG for s in slugs), slug
    for t in TEMPLATES:
        for day in t["days_spec"]:
            for slot in day["slots"]:
                assert slot["candidates"], (t["id"], slot["pattern"])
                assert all(c in CATALOG for c in slot["candidates"]), t["id"]
    for ladder_id, ladder in LADDERS.items():
        assert all(s in CATALOG for s in ladder["steps"]), ladder_id


def test_unverified_flags_follow_the_catalog_review_list():
    unsettled = {s for s, e in CATALOG.items() if not e["verified"]}
    assert {"pallof_press", "archer_push_up", "copenhagen_plank"} <= unsettled
    assert "barbell_bench_press" not in unsettled
    assert all(not t.get("verified", False) for t in TEMPLATES)  # ревью тренером не проводилось


def test_templates_are_consistent():
    assert [t["id"] for t in TEMPLATES] == [f"T{i:02d}" for i in range(1, 23)]
    for t in TEMPLATES:
        if not t["engine_ready"]:
            assert t["fallback"] and BY_ID[t["fallback"]]["engine_ready"], t["id"]
        assert set(t["levels"]) <= set(LEVELS)
        assert t["days"] == sorted(t["days"])
        if t["id"] != "T18":
            assert t["days_spec"], t["id"]


def test_matrix_covers_every_answer_exactly_once():
    rows = [r for r in matrix.build_matrix() if r["condition"] is None]
    keys = [(r["goal"], r["days"], r["level"], r["inventory"]) for r in rows]
    assert len(keys) == len(set(keys)) == 6 * 5 * 3 * 5
    assert set(keys) == set(product(matrix.GOALS, matrix.DAYS, LEVELS, matrix.INVENTORY_PROFILES))
    assert all(r["templates"] and all(t in BY_ID for t in r["templates"]) for r in rows)


def _resolve(template_id: str, inventory: str, level: str, flags=None):
    spec = BY_ID[template_id]
    if spec.get("base_by_days"):
        spec = BY_ID["T09"]  # составной шаблон проверяется через базовые
    return resolver.resolve_template(
        spec, CATALOG, resolver.inventory_items(inventory), level, flags
    )


def test_every_answer_gives_a_program_without_empty_slots():
    """Гейт фазы 2: любой ответ онбординга даёт шаблон, у которого заполнены все слоты."""
    rows = matrix.build_matrix()
    checked = set()
    for r in rows:
        if r["condition"] is not None:
            continue
        for tid in r["templates"]:
            if tid == "T18":
                spec = BY_ID["T18"]  # составной: база зависит от инвентаря и числа дней
                base = spec["base_home"].get(r["inventory"]) or spec["base_by_days"][str(r["days"])]
                result = _resolve(base, r["inventory"], r["level"])
                assert not result["empty"], (tid, base, r["inventory"], result["empty"])
                continue
            result = _resolve(tid, r["inventory"], r["level"])
            assert not result["empty"], (tid, r["inventory"], r["level"], result["empty"])
            checked.add((tid, r["inventory"]))
    # шаблоны, не заданные в матрице как основные, тоже должны разрешаться на своих инвентарях
    for t in TEMPLATES:
        if t["id"] == "T18":
            continue
        for inventory in t["inventory"]:
            for level in t["levels"]:
                assert not _resolve(t["id"], inventory, level)["empty"], (t["id"], inventory, level)


def test_condition_rows_and_recommend():
    rows = matrix.build_matrix()
    plain = matrix.recommend(rows, "mass", 4, "intermediate", "gym")
    assert plain["primary"] == "T08" and plain["then"] == []
    assert matrix.recommend(rows, "mass", 4, "intermediate", "gym", {"short30"})["primary"] == "T13"
    broken = matrix.recommend(rows, "mass", 4, "intermediate", "gym", {"break"})
    assert broken["primary"] == "T14" and broken["then"] == ["T08"]
    older = matrix.recommend(rows, "mass", 3, "beginner", "gym", {"age50", "break"})
    assert older["primary"] == "T14" and older["then"][0] == "T20"
    assert matrix.recommend(rows, "mass", 4, "intermediate", "gym", {"split"})["primary"] == "T12"
    assert matrix.recommend(rows, "mass", 3, "beginner", "dumbbells")["primary"] == "T15"
    assert matrix.recommend(rows, "strength", 3, "advanced", "gym")["primary"] == "T21"
    assert matrix.recommend(rows, "strength", 5, "beginner", "gym")["reasons"]


# ---------- подбор упражнения ----------


def test_slot_resolution_respects_inventory_level_and_flags():
    pull = {"pattern": "vertical_pull", "candidates": ["pull_up", "lat_pulldown_wide"]}
    gym = resolver.resolve_slot(pull, CATALOG, resolver.inventory_items("gym"), "beginner")
    assert gym.slug == "pull_up" and gym.via == "candidate"
    assert resolver.resolve_slot(
        pull, CATALOG, resolver.inventory_items("bodyweight"), "beginner"
    ).via in (
        "neighbour_pattern",
        "pattern",
    )
    squat = {"pattern": "squat", "candidates": ["back_squat_high_bar", "goblet_squat"]}
    knee = resolver.blocked_flags({"knee"})
    sq = resolver.resolve_slot(
        squat, CATALOG, resolver.inventory_items("gym"), "intermediate", knee
    )
    assert not set(CATALOG[sq.slug]["caution_flags"]) & knee
    no_barbell = resolver.resolve_slot(
        squat, CATALOG, resolver.inventory_items("dumbbells"), "beginner"
    )
    assert no_barbell.slug == "goblet_squat"


def test_equipment_alternatives_are_all_or_nothing():
    bench_press = CATALOG["barbell_bench_press"]
    assert resolver.available(bench_press, resolver.inventory_items("gym"))
    assert not resolver.available(bench_press, resolver.inventory_items("dumbbells"))
    assert resolver.available(
        bench_press, resolver.inventory_items("dumbbells", {"barbell", "bench", "rack"})
    )
    goblet = CATALOG["goblet_squat"]  # гантель ИЛИ гиря
    assert resolver.available(goblet, {"kettlebell"}) and resolver.available(goblet, {"dumbbell"})


# ---------- импорт в БД ----------


@pytest.fixture
def seeded(client):
    with client.session_factory() as session:
        stats = seed_catalog(session)
    return stats


def test_seed_is_idempotent_and_keeps_legacy_ids(client):
    with client.session_factory() as s:
        s.add_all(
            [
                Exercise(name="Жим лёжа", category="strength", muscle_group="chest"),
                Exercise(name="Планка", category="strength", muscle_group="core"),
                Exercise(name="Бег", category="cardio", muscle_group="full_body"),
            ]
        )
        s.commit()
        first = seed_catalog(s)
        second = seed_catalog(s)
        assert first["matched_legacy"] == 2 and first["created"] == 372
        assert second["created"] == 0 and second["updated"] == 374
        assert s.scalar(select(func.count(Exercise.id))) == 375  # 374 + прежний «Бег»
        bench = s.get(Exercise, 1)
        assert bench.slug == "barbell_bench_press" and bench.name == "Жим штанги лёжа"
        assert s.scalar(select(func.count(ProgramTemplate.id))) == 22
        assert s.scalar(select(func.count(TemplateMatrix.id))) == len(matrix.build_matrix())
        assert (
            s.scalar(select(func.count(ExerciseMuscle.id))) > 700
        )  # связей не удваивается при повторе


# ---------- API каталога ----------


def test_catalog_requires_login(client, seeded):
    for path in (
        "/catalog/groups",
        "/catalog/exercises",
        "/catalog/exercises/1",
        "/programs",
        "/programs/T01",
    ):
        assert client.get(path).status_code == 401


def test_search_filters_and_counts(client, auth_headers, seeded):
    headers = auth_headers()
    everything = client.get("/catalog/exercises?limit=5", headers=headers).json()
    assert (
        everything["catalog_total"] == 374
        and everything["total"] == 374
        and len(everything["items"]) == 5
    )
    by_name = client.get("/catalog/exercises?q=румын", headers=headers).json()
    assert by_name["total"] >= 3 and all(
        "румын" in i["name"].lower() or i["slug"] for i in by_name["items"]
    )
    chest = client.get("/catalog/exercises?group=chest&limit=200", headers=headers).json()
    assert 20 < chest["total"] < 374 and all("chest" in i["ui_groups"] for i in chest["items"])
    pattern = client.get("/catalog/exercises?pattern=hinge&limit=200", headers=headers).json()
    assert pattern["total"] == 21 and {i["pattern"] for i in pattern["items"]} == {"hinge"}
    page2 = client.get("/catalog/exercises?limit=5&offset=5", headers=headers).json()
    assert [i["id"] for i in page2["items"]] != [i["id"] for i in everything["items"]]
    assert client.get("/catalog/exercises?level=expert", headers=headers).status_code == 422
    groups = client.get("/catalog/groups", headers=headers).json()
    assert {g["key"] for g in groups} >= {"chest", "quads", "glutes", "abs"} and all(
        g["count"] > 0 for g in groups
    )


def test_fits_filter_uses_the_profile_inventory(client, auth_headers, seeded):
    headers = auth_headers()
    client.post(
        "/characters",
        json={"name": "Игрок", "equipment": "none", "experience": "beginner"},
        headers=headers,
    )
    fits = client.get("/catalog/exercises?fits=true&limit=200", headers=headers).json()
    assert 0 < fits["total"] < 374 and all(i["fits_you"] for i in fits["items"])
    names = {i["slug"] for i in fits["items"]}
    assert "push_up" in names and "barbell_bench_press" not in names


def test_exercise_card_has_muscles_flags_and_substitutes(client, auth_headers, seeded):
    headers = auth_headers()
    squat = client.get("/catalog/exercises?q=back_squat_high_bar", headers=headers).json()["items"][
        0
    ]
    card = client.get(f"/catalog/exercises/{squat['id']}", headers=headers).json()
    assert (
        card["slug"] == "back_squat_high_bar" and card["name_en"] and card["load_type"] == "barbell"
    )
    assert card["load_increment_kg"] == 2.5 and card["e1rm"] == "yes"
    roles = {m["role"] for m in card["muscles"]}
    assert "primary" in roles and card["muscles"][0]["volume_weight"] == 1.0
    assert "Осевая нагрузка на позвоночник" in card["flags"]
    assert card["equipment_names"] == [["штанга", "стойки"]]
    assert card["substitutes"] and all(s["slug"] != card["slug"] for s in card["substitutes"])
    assert card["cues"] == [] and card["media"] == []
    assert client.get("/catalog/exercises/99999", headers=headers).status_code == 404


def test_substitutes_follow_scenario_inventory_and_complaints(client, auth_headers, seeded):
    headers = auth_headers()
    squat = client.get("/catalog/exercises?q=back_squat_high_bar", headers=headers).json()["items"][
        0
    ]["id"]
    base = f"/catalog/exercises/{squat}/substitutes"
    no_barbell = client.get(f"{base}?scenario=noBB&inventory=dumbbells", headers=headers).json()
    assert no_barbell and no_barbell[0]["reason"] == "explicit"
    assert {s["slug"] for s in no_barbell} <= {
        s["slug"] for s in CATALOG.values() if resolver.available(s, {"dumbbell", "bodyweight"})
    }
    knee = client.get(f"{base}?scenario=KNEE&zones=knee", headers=headers).json()
    assert knee and all(
        not set(CATALOG[s["slug"]]["caution_flags"]) & resolver.ZONE_FLAGS["knee"] for s in knee
    )
    assert client.get(f"{base}?scenario=moon", headers=headers).status_code == 422
    assert client.get("/catalog/exercises/99999/substitutes", headers=headers).status_code == 404


# ---------- API программ ----------


def test_programs_list_puts_recommended_first(client, auth_headers, seeded):
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
    items = client.get("/programs", headers=headers).json()
    assert len(items) == 22
    assert items[0]["id"] == "T08" and items[0]["fits_you"] is True
    assert [i["id"] for i in items if i["fits_you"]] == ["T08"]
    assert next(i for i in items if i["id"] == "T12")["on_request_only"] is True


def test_recommendation_from_profile_and_overrides(client, auth_headers, seeded):
    headers = auth_headers()
    body = {
        "name": "Игрок",
        "goal": "strength",
        "experience": "beginner",
        "workouts_per_week": 3,
        "equipment": "gym",
    }
    client.post("/characters", json=body, headers=headers)
    rec = client.get("/programs/recommend", headers=headers).json()
    assert rec["primary"]["id"] == "T02" and [t["id"] for t in rec["then"]] == ["T03"]
    assert (
        rec["primary"]["engine_ready"] is False
        and rec["usable_id"] == "T09"
        and "T09" in rec["usable_note"]
    )
    assert rec["inputs"]["goal"] == "strength" and rec["inputs"]["conditions"] == []

    short = client.get("/programs/recommend?short=true", headers=headers).json()
    assert short["primary"]["id"] == "T13" and short["usable_note"] is None
    home = client.get("/programs/recommend?inventory=dumbbells&goal=mass", headers=headers).json()
    assert home["primary"]["id"] == "T15"
    assert client.get("/programs/recommend?goal=chess", headers=headers).status_code == 422


def test_break_and_age_add_conditions(client, auth_headers, seeded):
    headers = auth_headers()
    client.post(
        "/characters",
        json={
            "name": "Игрок",
            "goal": "mass",
            "experience": "intermediate",
            "workouts_per_week": 4,
            "age": 55,
        },
        headers=headers,
    )
    day = (datetime.now(UTC) - timedelta(days=30)).date().isoformat()
    wid = client.post("/workouts", json={"date": day}, headers=headers).json()["id"]
    exercise = client.get("/catalog/exercises?q=push_up", headers=headers).json()["items"][0]["id"]
    client.post(
        f"/workouts/{wid}/sets", json={"exercise_id": exercise, "reps": 10}, headers=headers
    )
    client.post(f"/workouts/{wid}/finish", headers=headers)
    rec = client.get("/programs/recommend", headers=headers).json()
    assert rec["primary"]["id"] == "T14" and rec["then"][0]["id"] == "T20"
    assert set(rec["inputs"]["conditions"]) == {"age50", "break"}


def test_program_detail_resolves_exercises_for_the_inventory(client, auth_headers, seeded):
    headers = auth_headers()
    gym = client.get("/programs/T08?inventory=gym&level=intermediate", headers=headers).json()
    assert gym["name"] == "Верх/низ: масса" and gym["empty_slots"] == [] and len(gym["days"]) == 4
    first = gym["days"][0]["slots"][0]
    assert (
        first["exercise_slug"] == "barbell_bench_press"
        and first["sets"] == [3, 3]
        and first["reps"] == [6, 10]
    )
    assert gym["volume"] and gym["volume"][0]["sets"] >= gym["volume"][-1]["sets"]
    assert {v["group"] for v in gym["volume"]} >= {"chest", "quads", "hamstrings"}

    home = client.get("/programs/T08?inventory=dumbbells&level=beginner", headers=headers).json()
    assert home["empty_slots"] == []
    slugs = {s["exercise_slug"] for d in home["days"] for s in d["slots"]}
    assert "barbell_bench_press" not in slugs and all(
        resolver.available(CATALOG[s], {"dumbbell", "bodyweight"}) for s in slugs
    )
    assert client.get("/programs/T99", headers=headers).status_code == 404


def test_program_detail_filters_by_complaints_and_expands_composites(client, auth_headers, seeded):
    headers = auth_headers()
    knee = client.get("/programs/T09?zones=knee&level=intermediate", headers=headers).json()
    for day in knee["days"]:
        for slot in day["slots"]:
            if slot["exercise_slug"]:
                assert (
                    not set(CATALOG[slot["exercise_slug"]]["caution_flags"])
                    & resolver.ZONE_FLAGS["knee"]
                )
    loss = client.get("/programs/T18?days=3&inventory=gym", headers=headers).json()
    assert loss["base_template"] == "T09" and loss["days"] and loss["cardio"]["zone2"]
    assert "дефицит" in loss["warning"]
    home = client.get("/programs/T18?days=3&inventory=bodyweight", headers=headers).json()
    assert home["base_template"] == "T16" and home["empty_slots"] == []


def test_unsupported_progression_is_reported(client, auth_headers, seeded):
    headers = auth_headers()
    detail = client.get("/programs/T04", headers=headers).json()
    assert detail["engine_ready"] is False and detail["fallback"] == "T07"
    assert detail["week_scheme"] and detail["verified"] is False


def test_starter_plan_comes_from_the_recommended_program(client, auth_headers, seeded):
    headers = auth_headers()
    assert client.get("/plan", headers=headers).json()["items"] == []
    body = {
        "name": "Игрок",
        "goal": "mass",
        "experience": "beginner",
        "workouts_per_week": 3,
        "equipment": "gym",
    }
    client.post("/characters", json=body, headers=headers)
    plan = client.get("/plan", headers=headers).json()
    assert plan["source"] == "starter" and 3 <= len(plan["items"]) <= 5
    with client.session_factory() as s:
        ids = {e.id: e for e in s.scalars(select(Exercise))}
    assert all(
        item["exercise_id"] in ids and item["target_weight_kg"] is None for item in plan["items"]
    )
    assert all(ids[item["exercise_id"]].category == "strength" for item in plan["items"])
    assert len({item["exercise_id"] for item in plan["items"]}) == len(plan["items"])
