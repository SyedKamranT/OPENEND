import json

from openend.benchmark import Instance
from openend.decision_diagnostic import trace
from openend.feedback_proposal import bounded_revision, requests, score_response
from openend.policy import REFERENCES, Policy


def test_revision_preserves_root_and_all_other_subtrees():
    bf = REFERENCES["best_fit"]
    assert bounded_revision(bf, bf)
    assert bounded_revision(bf, Policy.from_object({"expression": ["neg", ["abs", "gap"]]}))
    assert not bounded_revision(bf, REFERENCES["worst_fit"])
    parent = Policy.from_object({"expression": ["add", "gap", "item"]})
    assert not bounded_revision(parent, Policy.from_object({"expression": ["add", "index", 1]}))


def test_feedback_conditions_share_seeds_parents_and_positive_examples(monkeypatch):
    import openend.feedback_proposal as module

    monkeypatch.setattr(
        module, "examples", lambda _: {"beneficial": ["positive"], "harmful": ["negative"]}
    )
    rows = requests([])
    assert len(rows) == 12
    for parent in ("best_fit", "historical_witness"):
        for seed in module.CONFIG["seeds"]:
            group = [r for r in rows if r["parent"] == parent and r["seed"] == seed]
            prompts = {r["arm"]: json.loads(r["request"]["prompt"]) for r in group}
            assert prompts["none"]["examples"] == []
            assert prompts["beneficial"]["examples"] == ["positive"]
            assert prompts["mixed"]["examples"] == ["positive", "negative"]
            for prompt in prompts.values():
                prompt.pop("examples")
            assert prompts["none"] == prompts["beneficial"] == prompts["mixed"]


def test_invalid_and_worsening_responses_keep_parent():
    row = {"parent": "best_fit"}
    assert score_response(row, {"status": "incomplete_response"}, [])["selected_bins"] == 1476
    assert score_response(row, {"status": "ok", "text": "{}"}, [])["status"] == "invalid"
    traces = [trace(Instance("fixture", "uniform", 100, (60, 50, 30, 20, 40)))]
    response = {"status": "ok", "text": '{"expression":["neg",["neg","gap"]]}'}
    scored = score_response(row, response, traces)
    assert scored["regresses_parent"] and not scored["accepted"]
    assert scored["selected_bins"] == 1476
