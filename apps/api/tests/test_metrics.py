from datetime import timedelta


def make_character(client, headers):
    body = {"name": "Бодрый", "appearance": "warrior"}
    assert client.post("/characters", json=body, headers=headers).status_code == 201


def put(client, headers, weight, **extra):
    return client.put("/metrics/weight", json={"weight_kg": weight, **extra}, headers=headers)


def test_weight_gives_xp_once_per_day(client, auth_headers, clock):
    headers = auth_headers()
    make_character(client, headers)
    first = put(client, headers, 80.5)
    assert first.status_code == 200
    assert first.json() == {"date": "2026-10-20", "weight_kg": 80.5, "xp_gained": 5}

    again = put(client, headers, 80.0)
    assert again.json()["xp_gained"] == 0
    assert again.json()["weight_kg"] == 80.0

    entries = client.get("/metrics/weight", headers=headers).json()
    assert entries == [{"date": "2026-10-20", "weight_kg": 80.0}]
    assert client.get("/me", headers=headers).json()["character"]["xp"] == 5

    clock.now += timedelta(days=1)
    assert put(client, headers, 79.8).json()["xp_gained"] == 5


def test_backdated_entry_saved_without_xp(client, auth_headers, clock):
    headers = auth_headers()
    make_character(client, headers)
    saved = put(client, headers, 82, date="2026-10-01")
    assert saved.status_code == 200 and saved.json()["xp_gained"] == 0
    assert client.get("/me", headers=headers).json()["character"]["xp"] == 0


def test_invalid_dates_and_values(client, auth_headers, clock):
    headers = auth_headers()
    assert put(client, headers, 80, date="2026-10-21").status_code == 422  # будущее
    assert put(client, headers, 80, date="2024-01-01").status_code == 422  # слишком давно
    assert put(client, headers, 5).status_code == 422
    assert put(client, headers, 900).status_code == 422
    assert put(client, headers, "много").status_code == 422


def test_without_character_no_xp(client, auth_headers, clock):
    headers = auth_headers()
    assert put(client, headers, 80).json()["xp_gained"] == 0


def test_list_is_sorted_and_filtered(client, auth_headers, clock):
    headers = auth_headers()
    for day, weight in (("2026-10-10", 81), ("2026-06-01", 83), ("2026-10-18", 80)):
        put(client, headers, weight, date=day)

    default = client.get("/metrics/weight", headers=headers).json()
    assert [e["date"] for e in default] == ["2026-10-10", "2026-10-18"]  # последние 90 дней

    ranged = client.get(
        "/metrics/weight", params={"from": "2026-05-01", "to": "2026-10-12"}, headers=headers
    ).json()
    assert [e["date"] for e in ranged] == ["2026-06-01", "2026-10-10"]

    bad = client.get("/metrics/weight", params={"from": "2026-10-12", "to": "2026-10-01"},
                     headers=headers)
    assert bad.status_code == 422


def test_weights_are_private(client, auth_headers, clock):
    a = auth_headers({"id": 1, "username": "a"})
    b = auth_headers({"id": 2, "username": "b"})
    put(client, a, 90)
    assert client.get("/metrics/weight", headers=b).json() == []


def test_weight_requires_auth(client):
    assert client.get("/metrics/weight").status_code == 401
    assert client.put("/metrics/weight", json={"weight_kg": 80}).status_code == 401
