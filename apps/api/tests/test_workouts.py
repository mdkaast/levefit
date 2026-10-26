def new_workout(client, headers, **body):
    response = client.post("/workouts", json=body, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def add_set(client, headers, workout_id, **body):
    return client.post(f"/workouts/{workout_id}/sets", json=body, headers=headers)


def test_exercise_list_has_shared_and_own_only(client, auth_headers, exercises):
    a = auth_headers({"id": 1, "username": "a"})
    b = auth_headers({"id": 2, "username": "b"})
    created = client.post(
        "/exercises",
        json={"name": "Моё", "category": "strength", "muscle_group": "arms"},
        headers=a,
    )
    assert created.status_code == 201
    names_a = {e["name"] for e in client.get("/exercises", headers=a).json()}
    names_b = {e["name"] for e in client.get("/exercises", headers=b).json()}
    assert "Моё" in names_a and "Жим лёжа" in names_a
    assert "Моё" not in names_b and "Жим лёжа" in names_b


def test_full_workout_flow(client, auth_headers, exercises):
    headers = auth_headers()
    wid = new_workout(client, headers, title="Грудь")
    strength = exercises["strength"]
    for reps in (8, 7, 5):
        r = add_set(client, headers, wid, exercise_id=strength, weight_kg=80, reps=reps, rir=2)
        assert r.status_code == 201
    assert r.json()["set_no"] == 3

    finished = client.post(f"/workouts/{wid}/finish", json={"duration_min": 55}, headers=headers)
    assert finished.status_code == 200
    body = finished.json()
    assert body["status"] == "finished" and body["duration_min"] == 55
    assert [s["reps"] for s in body["sets"]] == [8, 7, 5]

    history = client.get("/workouts", headers=headers).json()
    assert len(history) == 1
    assert history[0]["title"] == "Грудь" and history[0]["sets_count"] == 3


def test_set_numbers_are_per_exercise(client, auth_headers, exercises):
    headers = auth_headers()
    wid = new_workout(client, headers)
    add_set(client, headers, wid, exercise_id=exercises["strength"], reps=5)
    run = add_set(client, headers, wid, exercise_id=exercises["cardio"], duration_s=600)
    assert run.json()["set_no"] == 1


def test_finished_workout_is_locked(client, auth_headers, exercises):
    headers = auth_headers()
    wid = new_workout(client, headers)
    add_set(client, headers, wid, exercise_id=exercises["strength"], reps=5)
    client.post(f"/workouts/{wid}/finish", headers=headers)
    again = add_set(client, headers, wid, exercise_id=exercises["strength"], reps=5)
    assert again.status_code == 409
    assert client.post(f"/workouts/{wid}/finish", headers=headers).status_code == 409


def test_cannot_finish_empty_workout(client, auth_headers, exercises):
    headers = auth_headers()
    wid = new_workout(client, headers)
    assert client.post(f"/workouts/{wid}/finish", headers=headers).status_code == 409


def test_set_validation_by_category(client, auth_headers, exercises):
    headers = auth_headers()
    wid = new_workout(client, headers)
    assert add_set(client, headers, wid, exercise_id=exercises["strength"]).status_code == 422
    assert add_set(client, headers, wid, exercise_id=exercises["cardio"]).status_code == 422
    assert add_set(client, headers, wid, exercise_id=exercises["mobility"]).status_code == 422
    assert (
        add_set(client, headers, wid, exercise_id=exercises["strength"], reps=5, rir=11).status_code
        == 422
    )
    assert (
        add_set(
            client, headers, wid, exercise_id=exercises["strength"], reps=5, weight_kg=-1
        ).status_code
        == 422
    )
    assert add_set(client, headers, wid, exercise_id=9999, reps=5).status_code == 404


def test_other_users_data_is_hidden(client, auth_headers, exercises):
    a = auth_headers({"id": 1, "username": "a"})
    b = auth_headers({"id": 2, "username": "b"})
    wid = new_workout(client, a)
    own = client.post(
        "/exercises",
        json={"name": "Моё", "category": "strength", "muscle_group": "arms"},
        headers=a,
    ).json()["id"]

    assert client.get(f"/workouts/{wid}", headers=b).status_code == 404
    assert add_set(client, b, wid, exercise_id=exercises["strength"], reps=5).status_code == 404
    assert client.post(f"/workouts/{wid}/finish", headers=b).status_code == 404
    assert client.get("/workouts", headers=b).json() == []

    wid_b = new_workout(client, b)
    assert add_set(client, b, wid_b, exercise_id=own, reps=5).status_code == 404


def test_workouts_require_auth(client):
    assert client.get("/workouts").status_code == 401
    assert client.get("/exercises").status_code == 401


def test_finish_saves_notes(client, auth_headers, exercises):
    headers = auth_headers()
    wid = new_workout(client, headers)
    add_set(client, headers, wid, exercise_id=exercises["strength"], reps=5)
    finished = client.post(f"/workouts/{wid}/finish", json={"notes": "Легко"}, headers=headers)
    assert finished.json()["notes"] == "Легко"
    too_long = {"notes": "x" * 2001}
    wid2 = new_workout(client, headers)
    add_set(client, headers, wid2, exercise_id=exercises["strength"], reps=5)
    response = client.post(f"/workouts/{wid2}/finish", json=too_long, headers=headers)
    assert response.status_code == 422
