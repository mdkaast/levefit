"""Питание: данные, цель и защитные правила, дневник, рецепты (фаза 4)."""

import pytest

from app import nutrition_calc as calc
from app.content.foods_data import FOODS
from app.content.recipes_data import RECIPES
from app.content.seed_nutrition import seed_nutrition
from app.nutrition_recipes import auto_tags, macros, suggest

FOOD = {f[0]: f for f in FOODS}


# ---------- данные ----------


def test_food_slugs_are_unique_and_values_are_sane():
    assert len({f[0] for f in FOODS}) == len(FOODS) >= 120
    for slug, name, _group, kcal, protein, fat, carbs, piece_g, piece_name in FOODS:
        assert name and 0 <= kcal <= 900 and min(protein, fat, carbs) >= 0, slug
        assert protein + fat + carbs <= 100.5, slug
        assert (piece_g is None) == (piece_name is None), slug


def test_calories_agree_with_macros():
    """Ккал должны сходиться с 4·Б + 9·Ж + 4·У: так ловятся опечатки в таблице."""
    for slug, _n, _g, kcal, protein, fat, carbs, *_ in FOODS:
        atwater = 4 * protein + 9 * fat + 4 * carbs
        assert abs(kcal - atwater) <= max(0.15 * kcal, 10), (slug, kcal, atwater)


def test_recipes_reference_known_foods_and_have_a_base_of_100():
    assert len(RECIPES) >= 100 and len({r[0] for r in RECIPES}) == len(RECIPES)
    for slug, name, minutes, servings, meal, items, steps in RECIPES:
        assert name and minutes > 0 and servings >= 1, slug
        assert meal in {"breakfast", "lunch", "dinner", "snack"}, slug
        assert items and all(food in FOOD and grams > 0 for food, grams in items), slug
        assert steps.strip(), slug


def test_recipe_macros_per_serving_are_plausible():
    for slug, _n, _minutes, servings, _meal, items, _s in RECIPES:
        per = macros(
            [
                (
                    {
                        "kcal": FOOD[f][3],
                        "protein": FOOD[f][4],
                        "fat": FOOD[f][5],
                        "carbs": FOOD[f][6],
                    },
                    g,
                )
                for f, g in items
            ],
            servings,
        )
        assert 80 <= per["kcal"] <= 1100, (slug, per)
        assert per["protein"] <= 90 and per["fat"] <= 80, (slug, per)


def test_auto_tags():
    high_protein = {"kcal": 450, "protein": 40, "fat": 10, "carbs": 40}
    assert {"protein", "post", "light"} - set(auto_tags(high_protein, 15, {"meat"})) == {"light"}
    assert "vegetarian" not in auto_tags(high_protein, 15, {"meat"})
    assert "vegetarian" in auto_tags(high_protein, 15, {"dairy"})
    assert "quick" in auto_tags(high_protein, 15, set()) and "quick" not in auto_tags(
        high_protein, 45, set()
    )
    assert "post_run" in auto_tags({"kcal": 600, "protein": 25, "fat": 10, "carbs": 80}, 20, set())


# ---------- цель и защитные правила ----------

MAN = calc.Profile(sex="male", age=30, height_cm=180, weight_kg=80, lifestyle="light")
WOMAN = calc.Profile(sex="female", age=30, height_cm=165, weight_kg=60, lifestyle="sedentary")


def test_bmr_and_maintenance():
    assert calc.bmr("male", 80, 180, 30) == 1780
    goal = calc.compute(MAN, "maintain", 0, [])
    assert goal and goal.bmr == 1780 and goal.tdee == 2450 and goal.kcal == 2450
    assert goal.protein_g == 144 and goal.fat_g == 80  # 1,8 и 1,0 г на кг
    assert goal.carbs_g == round((goal.kcal - 144 * 4 - 80 * 9) / 4)


def test_gain_and_lose_directions():
    maintain = calc.compute(MAN, "maintain", 0, [])
    gain = calc.compute(MAN, "gain", 0, [])
    lose = calc.compute(MAN, "lose", 0, [])
    assert gain.kcal > maintain.kcal > lose.kcal
    assert lose.delta_kcal < 0 and -lose.delta_kcal <= 0.2 * lose.tdee  # дефицит умеренный


def test_calories_never_go_below_floor():
    small = calc.Profile(sex="female", age=45, height_cm=155, weight_kg=48, lifestyle="sedentary")
    goal = calc.compute(small, "lose", -300, [])
    assert goal.kcal >= goal.floor and goal.floor >= 1200
    assert goal.carbs_g >= 0


def test_manual_adjust_is_stepped_and_limited():
    assert calc.clamp_adjust(120) == 100 and calc.clamp_adjust(999) == 300
    assert calc.clamp_adjust(-999) == -300
    plus = calc.compute(MAN, "maintain", 100, [])
    assert plus.kcal == calc.compute(MAN, "maintain", 0, []).kcal + 100


@pytest.mark.parametrize(
    "profile,flags,reason",
    [
        (MAN, ["eating_disorder"], None),
        (WOMAN, ["pregnant_or_nursing"], None),
        (WOMAN, ["fainting_or_amenorrhea"], None),
        (calc.Profile("male", 30, 180, 55, "light"), [], "low_bmi"),
        (calc.Profile("male", 16, 175, 70, "light"), [], "minor"),
    ],
)
def test_deficit_is_never_offered_when_risk_signs_exist(profile, flags, reason):
    assert calc.blocks_for(profile, flags)
    if reason:
        assert reason in calc.blocks_for(profile, flags)
    goal = calc.compute(profile, "lose", 0, flags)
    maintain = calc.compute(profile, "maintain", 0, flags)
    assert goal.mode == "maintain" and goal.kcal == maintain.kcal
    assert any("врач" in note for note in goal.notes)


def test_incomplete_profile_gives_no_goal():
    assert calc.compute(calc.Profile("male", None, 180, 80), "maintain", 0, []) is None
    assert calc.compute(calc.Profile("male", 30, 180, None), "maintain", 0, []) is None


def test_fast_weight_loss_gets_a_hint():
    assert calc.weight_trend_hint([79, 79], [81, 81]) is not None
    assert calc.weight_trend_hint([80.8, 80.9], [81, 81]) is None
    assert calc.weight_trend_hint([80], [81, 81]) is None


def test_suggest_respects_remaining_and_explains():
    recipes = [
        {"id": 1, "name": "Лёгкий", "kcal": 300, "protein": 25, "tags": ["protein"]},
        {"id": 2, "name": "Огромный", "kcal": 1200, "protein": 60, "tags": ["protein"]},
        {"id": 3, "name": "После бега", "kcal": 550, "protein": 30, "tags": ["post_run", "post"]},
    ]
    picked = suggest(recipes, 700, 40, None, False)
    assert [r["id"] for r in picked] and 2 not in [r["id"] for r in picked]
    assert all(r["reason"].startswith("Подходит, так как") for r in picked)
    run = suggest(recipes, 700, 40, "after", True)
    assert run[0]["id"] == 3 and "после бега" in run[0]["reason"]


# ---------- API ----------


@pytest.fixture
def nutri(client, auth_headers):
    with client.session_factory() as session:
        seed_nutrition(session)
    headers = auth_headers()
    client.post(
        "/characters",
        json={
            "name": "Игрок",
            "gender": "male",
            "age": 30,
            "height_cm": 180,
            "weight_kg": 80,
            "lifestyle": "light",
            "goal": "mass",
            "experience": "intermediate",
        },
        headers=headers,
    )
    client.h = headers
    return client


def food_id(client, query):
    items = client.get("/nutrition/foods", params={"q": query}, headers=client.h).json()["items"]
    return items[0]["id"]


def test_seed_is_idempotent(client):
    with client.session_factory() as s:
        first = seed_nutrition(s)
        second = seed_nutrition(s)
    assert first == second == {"foods": len(FOODS), "recipes": len(RECIPES)}
    foods = client.get("/nutrition/foods", params={"limit": 100})
    assert foods.status_code == 401  # без входа недоступно


def test_goal_defaults_and_save(nutri):
    state = nutri.get("/nutrition/goal", headers=nutri.h).json()
    assert (
        state["complete"] and state["goal"]["kcal"] == 2450 and state["goal"]["mode"] == "maintain"
    )
    assert state["options"]["lose"] < state["options"]["maintain"] < state["options"]["gain"]
    assert state["lose_blocked"] is False and state["goal"]["assumptions"]
    saved = nutri.put(
        "/nutrition/goal", json={"mode": "gain", "adjust_kcal": 50}, headers=nutri.h
    ).json()
    assert saved["goal"]["mode"] == "gain" and saved["adjust_kcal"] == 50


def test_lose_is_refused_when_screening_flag_is_set(nutri):
    r = nutri.put(
        "/nutrition/goal",
        json={"mode": "lose", "restrictions": ["eating_disorder"]},
        headers=nutri.h,
    )
    assert r.status_code == 422 and r.json()["detail"] == "lose_blocked"
    ok = nutri.put(
        "/nutrition/goal",
        json={"mode": "maintain", "restrictions": ["eating_disorder"]},
        headers=nutri.h,
    ).json()
    assert ok["lose_blocked"] and ok["goal"]["mode"] == "maintain"
    bad = nutri.put(
        "/nutrition/goal", json={"mode": "maintain", "restrictions": ["x"]}, headers=nutri.h
    )
    assert bad.status_code == 422


def test_goal_without_body_data_is_incomplete(client, auth_headers):
    with client.session_factory() as s:
        seed_nutrition(s)
    headers = auth_headers({"id": 2002, "username": "bare"})
    client.post("/characters", json={"name": "Игрок"}, headers=headers)
    state = client.get("/nutrition/goal", headers=headers).json()
    assert state["complete"] is False and state["goal"] is None


def test_search_is_case_insensitive_and_filters_by_group(nutri):
    found = nutri.get("/nutrition/foods", params={"q": "ГРЕЧ"}, headers=nutri.h).json()["items"]
    assert found and all("греч" in f["name"].casefold() for f in found)
    dairy = nutri.get("/nutrition/foods", params={"group": "dairy", "limit": 100}, headers=nutri.h)
    assert dairy.json()["items"] and {f["group"] for f in dairy.json()["items"]} == {"dairy"}


def test_diary_add_edit_delete_and_totals(nutri):
    egg = food_id(nutri, "Яйцо куриное")
    r = nutri.post(
        "/nutrition/entries",
        json={"meal": "breakfast", "food_id": egg, "grams": 110},
        headers=nutri.h,
    )
    assert r.status_code == 201
    entry = r.json()
    assert entry["kcal"] == round(143 * 1.1) and entry["grams"] == 110
    day = nutri.get("/nutrition/day", headers=nutri.h).json()
    breakfast = next(m for m in day["meals"] if m["meal"] == "breakfast")
    assert len(breakfast["entries"]) == 1 and day["totals"]["kcal"] == entry["kcal"]
    assert day["remaining"]["kcal"] == day["goal"]["kcal"] - entry["kcal"]

    patched = nutri.patch(
        f"/nutrition/entries/{entry['id']}", json={"grams": 55, "meal": "lunch"}, headers=nutri.h
    ).json()
    assert patched["grams"] == 55 and patched["kcal"] == round(143 * 0.55)
    day = nutri.get("/nutrition/day", headers=nutri.h).json()
    assert next(m for m in day["meals"] if m["meal"] == "lunch")["entries"]
    assert nutri.delete(f"/nutrition/entries/{entry['id']}", headers=nutri.h).status_code == 204
    assert nutri.get("/nutrition/day", headers=nutri.h).json()["totals"]["kcal"] == 0


def test_entry_validation(nutri):
    egg = food_id(nutri, "Яйцо куриное")
    base = {"meal": "snack", "food_id": egg, "grams": 100}
    assert (
        nutri.post("/nutrition/entries", json={**base, "grams": 0}, headers=nutri.h).status_code
        == 422
    )
    assert (
        nutri.post("/nutrition/entries", json={**base, "meal": "x"}, headers=nutri.h).status_code
        == 422
    )
    assert (
        nutri.post("/nutrition/entries", json={"meal": "snack"}, headers=nutri.h).status_code == 422
    )
    both = {**base, "recipe_id": 1}
    assert nutri.post("/nutrition/entries", json=both, headers=nutri.h).status_code == 422
    far = {**base, "date": "2000-01-01"}
    assert nutri.post("/nutrition/entries", json=far, headers=nutri.h).status_code == 422
    missing = {**base, "food_id": 999999}
    assert nutri.post("/nutrition/entries", json=missing, headers=nutri.h).status_code == 404


def test_entries_are_private(nutri, auth_headers):
    egg = food_id(nutri, "Яйцо куриное")
    entry = nutri.post(
        "/nutrition/entries", json={"meal": "snack", "food_id": egg, "grams": 50}, headers=nutri.h
    ).json()
    other = auth_headers({"id": 3003, "username": "other"})
    nutri.post("/characters", json={"name": "Другой"}, headers=other)
    assert nutri.delete(f"/nutrition/entries/{entry['id']}", headers=other).status_code == 404
    assert (
        nutri.patch(
            f"/nutrition/entries/{entry['id']}", json={"grams": 10}, headers=other
        ).status_code
        == 404
    )
    assert nutri.get("/nutrition/day", headers=other).json()["totals"]["kcal"] == 0


def test_snapshot_keeps_history_when_food_changes(nutri):
    egg = food_id(nutri, "Яйцо куриное")
    nutri.post(
        "/nutrition/entries", json={"meal": "snack", "food_id": egg, "grams": 100}, headers=nutri.h
    )
    from app.models import Food

    with nutri.session_factory() as s:
        food = s.get(Food, egg)
        food.kcal = 999
        s.commit()
    assert nutri.get("/nutrition/day", headers=nutri.h).json()["totals"]["kcal"] == 143


def test_recent_and_frequent_foods(nutri):
    egg, oats = food_id(nutri, "Яйцо куриное"), food_id(nutri, "Овсяные хлопья")
    for _ in range(2):
        nutri.post(
            "/nutrition/entries",
            json={"meal": "snack", "food_id": egg, "grams": 60},
            headers=nutri.h,
        )
    nutri.post(
        "/nutrition/entries", json={"meal": "snack", "food_id": oats, "grams": 40}, headers=nutri.h
    )
    data = nutri.get("/nutrition/foods/recent", headers=nutri.h).json()
    assert data["frequent"][0]["id"] == egg and data["frequent"][0]["last_grams"] == 60
    assert data["recent"][0]["id"] == oats


def test_custom_food_is_private_and_validated(nutri, auth_headers):
    made = nutri.post(
        "/nutrition/foods",
        json={"name": "Йогурт лавандовый", "kcal": 80, "protein": 4, "fat": 3, "carbs": 9},
        headers=nutri.h,
    )
    assert made.status_code == 201 and made.json()["own"] is True
    assert any(
        f["name"] == "Йогурт лавандовый"
        for f in nutri.get("/nutrition/foods", params={"q": "лавандовый"}, headers=nutri.h).json()[
            "items"
        ]
    )
    other = auth_headers({"id": 4004, "username": "x"})
    assert (
        nutri.get("/nutrition/foods", params={"q": "лавандовый"}, headers=other).json()["items"]
        == []
    )
    too_much = {"name": "Невозможный", "kcal": 100, "protein": 60, "fat": 60, "carbs": 10}
    assert nutri.post("/nutrition/foods", json=too_much, headers=nutri.h).status_code == 422
    entry = {"meal": "snack", "food_id": made.json()["id"], "grams": 200}
    assert nutri.post("/nutrition/entries", json=entry, headers=other).status_code == 404


def test_recipes_list_filters_and_detail_scaling(nutri):
    listing = nutri.get("/nutrition/recipes", headers=nutri.h).json()
    assert listing["total"] >= 100 and {t["key"] for t in listing["tags"]} >= {"protein", "quick"}
    protein = nutri.get("/nutrition/recipes", params={"tag": "protein"}, headers=nutri.h).json()
    assert 0 < protein["total"] < listing["total"]
    assert all("protein" in r["tags"] for r in protein["items"])
    found = nutri.get("/nutrition/recipes", params={"q": "ОВСЯНКА"}, headers=nutri.h).json()
    assert found["total"] >= 1
    card = found["items"][0]
    one = nutri.get(f"/nutrition/recipes/{card['id']}", headers=nutri.h).json()
    three = nutri.get(
        f"/nutrition/recipes/{card['id']}", params={"servings": 3}, headers=nutri.h
    ).json()
    assert one["ingredients"] and three["steps"]
    assert three["ingredients"][0]["grams"] == pytest.approx(
        one["ingredients"][0]["grams"] * 3, rel=0.1
    )
    assert nutri.get("/nutrition/recipes/999999", headers=nutri.h).status_code == 404


def test_add_recipe_to_diary_scales_by_servings(nutri):
    card = nutri.get("/nutrition/recipes", params={"q": "Сырники"}, headers=nutri.h).json()[
        "items"
    ][0]
    r = nutri.post(
        "/nutrition/entries",
        json={"meal": "dinner", "recipe_id": card["id"], "servings": 2},
        headers=nutri.h,
    ).json()
    assert r["recipe_id"] == card["id"] and r["servings"] == 2
    assert abs(r["kcal"] - 2 * card["kcal"]) <= 2
    day = nutri.get("/nutrition/day", headers=nutri.h).json()
    assert any(m["meal"] == "dinner" and m["entries"] for m in day["meals"])


def test_suggestions_come_with_reasons_and_react_to_the_day(nutri):
    empty = nutri.get("/nutrition/recipes/suggest", headers=nutri.h).json()
    assert empty["summary"] and empty["items"]
    assert all(r["reason"].startswith("Подходит, так как") for r in empty["items"])
    big = nutri.get("/nutrition/recipes", params={"q": "Плов"}, headers=nutri.h).json()["items"][0]
    nutri.post(
        "/nutrition/entries",
        json={"meal": "lunch", "recipe_id": big["id"], "servings": 4},
        headers=nutri.h,
    )
    after = nutri.get("/nutrition/recipes/suggest", headers=nutri.h).json()
    assert after["summary"] != empty["summary"]
    run = nutri.get(
        "/nutrition/recipes/suggest",
        params={"training": "after", "direction": "running"},
        headers=nutri.h,
    ).json()
    assert run["items"]
    assert (
        nutri.get(
            "/nutrition/recipes/suggest", params={"training": "x"}, headers=nutri.h
        ).status_code
        == 422
    )


def test_neutral_language_when_over_target(nutri):
    plov = nutri.get("/nutrition/recipes", params={"q": "Плов"}, headers=nutri.h).json()["items"][0]
    nutri.post(
        "/nutrition/entries",
        json={"meal": "dinner", "recipe_id": plov["id"], "servings": 12},
        headers=nutri.h,
    )
    day = nutri.get("/nutrition/day", headers=nutri.h).json()
    assert day["remaining"]["kcal"] < 0
    text = " ".join(day["hints"]).casefold()
    assert "выше цели" in text and not any(
        w in text for w in ("превыш", "штраф", "плохо", "нельзя")
    )
