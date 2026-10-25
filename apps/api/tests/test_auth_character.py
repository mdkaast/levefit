from tests.conftest import make_init_data

CHARACTER = {"name": "  Бодрый  ", "appearance": "warrior", "workouts_per_week": 4}


def test_forged_init_data_rejected(client):
    forged = make_init_data(bot_token="attacker:TOKEN")
    response = client.post("/auth/telegram", json={"init_data": forged})
    assert response.status_code == 401


def test_me_requires_token(client):
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_first_login_creates_user_without_character(client, auth_headers):
    response = client.get("/me", headers=auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == "tester"
    assert body["character"] is None


def test_repeated_login_keeps_single_user(client, auth_headers):
    first = client.get("/me", headers=auth_headers()).json()["user"]["id"]
    second = client.get("/me", headers=auth_headers()).json()["user"]["id"]
    assert first == second


def test_create_character(client, auth_headers):
    headers = auth_headers()
    response = client.post("/characters", json=CHARACTER, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Бодрый"
    assert (body["level"], body["xp"]) == (1, 0)
    assert client.get("/me", headers=headers).json()["character"]["name"] == "Бодрый"


def test_second_character_conflicts(client, auth_headers):
    headers = auth_headers()
    client.post("/characters", json=CHARACTER, headers=headers)
    assert client.post("/characters", json=CHARACTER, headers=headers).status_code == 409


def test_character_validation(client, auth_headers):
    headers = auth_headers()
    for bad in (
        {**CHARACTER, "name": "   "},
        {**CHARACTER, "appearance": "dragon"},
        {**CHARACTER, "workouts_per_week": 0},
        {**CHARACTER, "workouts_per_week": 8},
        {**CHARACTER, "equipment": "moon"},
    ):
        assert client.post("/characters", json=bad, headers=headers).status_code == 422


def test_users_are_isolated(client, auth_headers):
    a = auth_headers({"id": 1, "username": "a"})
    b = auth_headers({"id": 2, "username": "b"})
    client.post("/characters", json=CHARACTER, headers=a)
    assert client.get("/me", headers=b).json()["character"] is None


def test_concurrent_first_login_does_not_fail(client, auth_headers, monkeypatch):
    """Гонка: пользователя уже создал параллельный запрос, а наша проверка этого не видела."""
    from sqlalchemy.orm import Session

    auth_headers()  # пользователь уже существует
    real_scalar = Session.scalar
    calls = []

    def blind_first_lookup(self, *args, **kwargs):
        calls.append(1)
        return None if len(calls) == 1 else real_scalar(self, *args, **kwargs)

    monkeypatch.setattr(Session, "scalar", blind_first_lookup)
    response = client.post("/auth/telegram", json={"init_data": make_init_data()})
    assert response.status_code == 200
