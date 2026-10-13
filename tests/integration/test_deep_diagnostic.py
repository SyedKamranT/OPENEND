import json
from pathlib import Path

import pytest

from openend import deep_diagnostic as deep
from openend.benchmark import make_suite, pack, reference_pack
from openend.numerical_audit import ExactPolicy, exact_score
from openend.policy import REFERENCES, Policy, _validate

ROOT = Path(__file__).resolve().parents[2]


def test_prospective_plan_respects_full_grammar_budget():
    first = list(deep.proposals())
    assert first == list(deep.proposals()) and len(first) == 4096
    for value in first:
        assert _validate(value["expression"]) <= 31
        Policy.from_object(value)


def test_small_diagnostic_replay_and_certificate_tamper(tmp_path, monkeypatch):
    monkeypatch.setitem(deep.CONFIG, "attempts", 8)
    output = tmp_path / "diagnostic"
    result = deep.run(output, ROOT)
    assert result["attempts"] == 8 and result["stop_reason"] == "attempt_limit"
    assert deep.replay(output)["attempts"] == 8
    certificates = json.loads((output / "certificates.json").read_text())
    certificates[0]["assignments"][0] = 99
    (output / "certificates.json").write_text(json.dumps(certificates))
    with pytest.raises(ValueError):
        deep.replay(output)


def test_witness_rule_distinguishes_small_gain_and_family_regression():
    baseline = {"total_bins": 1000, "family_bins": {"a": 500, "b": 500}}
    assert deep.improved({"total_bins": 999, "family_bins": {"a": 499, "b": 500}}, baseline)
    assert not deep.improved({"total_bins": 999, "family_bins": {"a": 526, "b": 473}}, baseline)
    assert not deep.improved(baseline, baseline)


def test_summary_selects_eligible_witness_over_lower_total_with_family_regression():
    rows = [
        {
            "index": 0,
            "score": {"total_bins": 990},
            "improved": False,
            "policy": {"expression": 0},
            "utility_success": False,
        },
        {
            "index": 1,
            "score": {"total_bins": 999},
            "improved": True,
            "policy": {"expression": "gap"},
            "utility_success": False,
        },
    ]
    assert deep.summary(rows, {})["best"] == rows[1]


def test_exact_interpreter_agrees_with_independent_reference_packers():
    for name, policy in REFERENCES.items():
        exact = ExactPolicy(policy.to_object()["expression"])
        for instance in make_suite("train", 1):
            assert pack(exact, instance) == reference_pack(name, instance)
    assert exact_score(["div", 1, 0], {}) == 0
    assert exact_score(["mul", 1000000, 2], {}) == 1000000


def test_cancellation_witness_algebra_on_exact_states():
    expression = [
        "add",
        ["neg", "gap"],
        ["max", ["mul", "item", ["sub", "remaining", "gap"]], "gap"],
    ]
    reduced = ["max", ["sub", ["mul", "item", "item"], "gap"], 0]
    original, simplified = ExactPolicy(expression), ExactPolicy(reduced)
    for instance in make_suite("train", 1):
        assert pack(original, instance) == pack(simplified, instance)
