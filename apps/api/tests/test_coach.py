import pytest

from app.adjust import llm_dependency
from app.ai.schema import RuleProposals
from app.config import settings
from app.game_rules import config as rules
from app.main import app
from app.models import AdjustmentFeedback, AiAdjustment
from tests.test_ai_adjust import FakeLLM, explanation, plan_for, setup_workout

ADMIN = {"X-Admin-Key": "admin-key"}


def patch_rule(client, rule_id, value):
    return client.patch(f"/admin/coach/rules/{rule_id}", json={"status": value}, headers=ADMIN)


class LearningLLM(FakeLLM):
    def __init__(self, *answers, proposals=()):
        super().__init__(*answers)
        self.proposals = list(proposals)
        self.stats = []

    def propose_rules(self, stats):
        self.stats.append(stats)
        return RuleProposals(rules=self.proposals)


@pytest.fixture(autouse=True)
def _admin_key(monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "admin-key")


@pytest.fixture
def use_llm(client):
    def _use(llm):
        app.dependency_overrides[llm_dependency] = lambda: llm
        return llm

    yield _use
    app.dependency_overrides.pop(llm_dependency, None)


def adjusted_workout(client, headers, bench):
    wid = setup_workout(client, headers, bench)
    r = client.post(f"/workouts/{wid}/adjust", json=plan_for(bench), headers=headers)
    assert r.status_code == 200
    return wid


def test_admin_endpoints_need_key(client, monkeypatch):
    assert client.get("/admin/coach/rules").status_code == 401
    assert client.get("/admin/coach/rules", headers={"X-Admin-Key": "x"}).status_code == 401
    monkeypatch.setattr(settings, "admin_api_key", "")
    assert client.get("/admin/coach/rules", headers={"X-Admin-Key": ""}).status_code == 401


def test_only_approved_rules_reach_the_prompt(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    text = "Не повышай вес новичкам"
    owner = client.post("/admin/coach/rules", json={"text": text}, headers=ADMIN)
    assert owner.status_code == 201 and owner.json()["status"] == "approved"
    with client.session_factory() as s:
        from app.models import CoachRule

        s.add(CoachRule(text="Черновик ИИ", status="proposed", source="ai"))
        s.commit()
    llm = use_llm(FakeLLM(explanation()))
    adjusted_workout(client, headers, bench)
    assert llm.snapshots[0]["context"]["coach_rules"] == ["Не повышай вес новичкам"]


def test_owner_approves_and_rejects(client):
    with client.session_factory() as s:
        from app.models import CoachRule

        s.add_all(
            [
                CoachRule(text="Правило один", status="proposed", source="ai"),
                CoachRule(text="Правило два", status="proposed", source="ai"),
            ]
        )
        s.commit()
    assert patch_rule(client, 1, "approved").json()["status"] == "approved"
    assert patch_rule(client, 2, "rejected").status_code == 200
    assert patch_rule(client, 9, "approved").status_code == 404
    assert patch_rule(client, 1, "proposed").status_code == 422
    listed = client.get("/admin/coach/rules?status_filter=approved", headers=ADMIN).json()
    assert [r["text"] for r in listed] == ["Правило один"]


def test_feedback_saved_and_overwritten(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    use_llm(FakeLLM(explanation()))
    wid = adjusted_workout(client, headers, bench)
    url = f"/workouts/{wid}/adjust/feedback"
    assert client.post(url, json={"rating": "too_hard"}, headers=headers).status_code == 204
    assert client.post(url, json={"rating": "fits"}, headers=headers).status_code == 204
    assert client.post(url, json={"rating": "bad"}, headers=headers).status_code == 422
    with client.session_factory() as s:
        rows = s.query(AdjustmentFeedback).all()
        assert [r.rating for r in rows] == ["fits"]


def test_feedback_only_for_own_recommendation(client, auth_headers, exercises, use_llm):
    owner = auth_headers({"id": 1, "first_name": "A"})
    other = auth_headers({"id": 2, "first_name": "B"})
    bench = exercises["strength"]
    use_llm(FakeLLM(explanation()))
    wid = adjusted_workout(client, owner, bench)
    url = f"/workouts/{wid}/adjust/feedback"
    assert client.post(url, json={"rating": "fits"}, headers=other).status_code == 404


def test_learn_creates_proposals(client, auth_headers, exercises, use_llm):
    headers = auth_headers()
    bench = exercises["strength"]
    proposals = ["Правило А", "Правило А", " ", "Б" * 600]
    llm = use_llm(LearningLLM(explanation(), proposals=proposals))
    adjusted_workout(client, headers, bench)
    assert client.post("/admin/coach/learn", headers=ADMIN).status_code == 409

    with client.session_factory() as s:
        adj = s.query(AiAdjustment).one()
        s.add(AdjustmentFeedback(adjustment_id=adj.id, rating="too_hard"))
        s.commit()
    import app.coach as coach

    rules.COACH_MIN_FEEDBACK_TO_LEARN, old = 1, rules.COACH_MIN_FEEDBACK_TO_LEARN
    try:
        response = client.post("/admin/coach/learn", headers=ADMIN)
    finally:
        rules.COACH_MIN_FEEDBACK_TO_LEARN = old
    assert coach  # модуль подключён
    assert response.status_code == 200
    created = response.json()
    assert [r["status"] for r in created] == ["proposed", "proposed"]
    assert created[0]["text"] == "Правило А" and created[0]["source"] == "ai"
    assert llm.stats[0]["by_decision"] == {"keep_weight": {"too_hard": 1}}
    # предложения сами в промпт не попадают
    assert client.get("/admin/coach/rules?status_filter=approved", headers=ADMIN).json() == []
