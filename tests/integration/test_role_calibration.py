import json
from pathlib import Path

from openend.backends import Proposal
from openend.benchmark import make_suite
from openend.policy import Policy
from openend.role_calibration import CASES, STATES, assess, replay, run


class Backend:
    def __init__(self, missing=False):
        self.calls = 0
        self.missing = missing

    def identity(self):
        return {"model": "scripted"}

    def generate(self, system, prompt, schema, seed):
        self.calls += 1
        assert "validation" not in prompt and "test" not in prompt
        policy = json.loads(prompt)["policy"]
        case = next(c for c in CASES if c["expression"] == policy["expression"])
        text = json.dumps(
            {
                "reference_class": case["label"],
                "original_choices": case["choices"],
                "revision": ["neg", "gap"],
                "revision_choices": [1, 2, 0],
            }
        )
        return Proposal(text, {} if self.missing else {"total_tokens": 100}, {}, "ok")


def test_hand_derived_oracles_and_false_claims():
    train = make_suite("train", 1)
    for case in CASES:
        policy = Policy.from_object({"expression": case["expression"]})
        assert [policy.choose(s["item"], s["remaining"], 100) for s in STATES] == case["choices"]
    result = assess(
        json.dumps(
            {
                "reference_class": "best_fit",
                "original_choices": [1, 2, 0],
                "revision": "gap",
                "revision_choices": [1, 2, 0],
            }
        ),
        CASES[0],
        train,
    )
    assert result["valid"]
    assert not result["classification_correct"]
    assert not result["original_predictions_correct"]
    assert not result["revision_predictions_correct"]


def test_run_and_replay(tmp_path):
    backend = Backend()
    result = run(tmp_path / "run", backend, Path.cwd())
    assert backend.calls == 6 and result["accepted"]
    assert result["tokens"] == 600
    assert replay(tmp_path / "run")["calls"] == 6


def test_unknown_usage_stops_without_acceptance(tmp_path):
    backend = Backend(missing=True)
    result = run(tmp_path / "run", backend, Path.cwd())
    assert backend.calls == 1 and not result["accepted"] and not result["complete"]
    assert replay(tmp_path / "run")["calls"] == 1


def test_duplicate_fields_rejected():
    assert assess('{"revision":0,"revision":1}', CASES[0], ()) == {"valid": False}
