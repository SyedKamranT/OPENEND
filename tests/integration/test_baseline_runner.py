import io
import json
from pathlib import Path

import pytest

from openend.artifacts import file_hash
from openend.backends import Proposal
from openend.baseline_recovery import audit_interruption
from openend.baseline_runner import load_config, parse_response, replay, run, run_condition
from openend.baseline_state import EohState, FunsearchState, candidate
from openend.benchmark import evaluate, make_suite
from openend.policy import REFERENCES

ROOT = Path(__file__).resolve().parents[2]


class Scripted:
    context = 8192

    def __init__(self, invalid=False, missing=False):
        self.invalid, self.missing, self.calls = invalid, missing, 0

    def identity(self):
        return {"model": "fixture", "model_digest": "fixed", "options": {"num_ctx": self.context}}

    def generate(self, system, prompt, schema, seed):
        assert "test/" not in prompt and "validation/" not in prompt
        self.calls += 1
        expression = (0, ["neg", "gap"], "gap")[self.calls % 3]
        value = {"expression": expression}
        if "thought" in schema["required"]:
            value["thought"] = "Rank feasible bins using the specified score."
        return Proposal(
            "invalid" if self.invalid else json.dumps(value),
            {} if self.missing else {"total_tokens": 100},
            {"model": "fixture@fixed"},
        )


def config():
    return {**load_config(ROOT / "configs/baseline_adapters_v1.json"), "per_family": 1}


def reference_candidates():
    train = make_suite("train", 1)
    return [candidate(p, evaluate(p, train), name) for name, p in REFERENCES.items()]


def test_eoh_batch_boundaries_and_all_operators():
    state = EohState(2, 1)
    proposals = reference_candidates()
    operations = []
    for i in range(12):
        request = state.request()
        operations.append(request["operator"])
        previous = state.population.copy()
        state.observe(request, proposals[i % 3])
        if i % 2 == 0 or i < 3:
            assert state.population == previous
    assert operations == ["i1"] * 4 + ["e1"] * 2 + ["e2"] * 2 + ["m1"] * 2 + ["m2"] * 2
    assert len(state.population) == 2


def test_funsearch_clusters_resets_and_founders():
    proposals = reference_candidates()
    state = FunsearchState(4, 3, proposals[0], 1)
    for i in range(3):
        request = state.request()
        result = state.observe(request, proposals[i])
    assert len(result["resets"]) == 2
    targets = {r["island"] for r in result["resets"]}
    for reset in result["resets"]:
        assert reset["founder_island"] not in targets
        assert state.islands[reset["island"]]["registrations"] == 1
        assert state.islands[reset["island"]]["best"]["id"] == reset["policy_id"]
    assert sum(x["registrations"] for x in state.islands) >= 4


def test_adapters_full_scripted_run_and_state_replay(tmp_path):
    output = tmp_path / "adapters"
    backend = Scripted()
    result = run(config(), backend, output, ROOT)
    assert result["status"] == "completed" and backend.calls == 72
    assert all(r["valid_policies"] == 24 and r["tokens_accounted"] == 2400 for r in result["runs"])
    assert replay(output) == {"replay": "matched", "calls": 72, "model_calls": 0}
    rows = json.loads((output / "runs.json").read_text())
    eoh = next(r for r in rows if r["method"] == "eoh_json")
    assert {e["selection"]["operator"] for e in eoh["events"]} == {"i1", "e1", "e2", "m1", "m2"}


def test_missing_usage_stops_entire_study(tmp_path):
    backend = Scripted(missing=True)
    output = tmp_path / "missing"
    result = run(config(), backend, output, ROOT)
    assert backend.calls == 1 and result["status"] == "incomplete"
    assert replay(output)["calls"] == 1


def test_failed_initialization_stops_eoh_without_free_seed():
    result = run_condition(
        config(), Scripted(invalid=True), "eoh_json", 42, make_suite("train", 1), io.StringIO()
    )
    assert len(result["events"]) == 8
    assert result["stop_reason"] == "empty_eoh_population"
    assert result["summary"]["tokens_accounted"] == 800


def test_budget_preflight_no_calls_and_nontraining_rejected():
    backend = Scripted()
    result = run_condition(
        {**config(), "tokens": 1}, backend, "independent", 42, make_suite("train", 1), io.StringIO()
    )
    assert result["stop_reason"] == "token_admission" and backend.calls == 0
    with pytest.raises(ValueError):
        run_condition(config(), backend, "independent", 42, make_suite("test", 1), io.StringIO())


@pytest.mark.parametrize(
    "text",
    [
        '{"expression":0,"expression":1}',
        '{"expression":0,"thought":""}',
        '{"expression":0,"thought":"ok","novelty":true}',
    ],
)
def test_eoh_rejects_malformed_contract(text):
    with pytest.raises(ValueError):
        parse_response(text, "eoh_json")


def test_interruption_replay_preserves_original_and_unknown_usage(tmp_path):
    class Interrupted(Scripted):
        def generate(self, *args):
            if self.calls == 26:
                raise RuntimeError("simulated interruption")
            return super().generate(*args)

    source = tmp_path / "source"
    backend = Interrupted()
    with pytest.raises(RuntimeError, match="simulated interruption"):
        run(config(), backend, source, ROOT)
    before = {p.name: file_hash(p) for p in source.iterdir()}
    report = audit_interruption(source, tmp_path / "audit")
    assert report["started_requests"] == 27
    assert report["recovered_responses"] == 26
    assert report["unknown_responses"] == 1
    assert report["pending_actual_usage"] is None
    assert report["pending_token_reservation"] > 0
    assert report["model_calls"] == 0 and backend.calls == 26
    assert before == {p.name: file_hash(p) for p in source.iterdir()}
    lines = (source / "events.jsonl").read_text().splitlines()
    corrupted = json.loads(lines[1])
    corrupted["tokens_accounted"] += 1
    lines[1] = json.dumps(corrupted)
    (source / "events.jsonl").write_text("\n".join(lines) + "\n")
    with pytest.raises(ValueError, match="journal replay mismatch"):
        audit_interruption(source, tmp_path / "corrupt-audit")


@pytest.mark.parametrize("method", ["independent", "eoh_json", "funsearch_json"])
@pytest.mark.parametrize("expression", [0.05, ["neg", ["neg", ["neg", ["neg", ["neg", "gap"]]]]]])
def test_baseline_rejects_evaluator_valid_but_proposal_invalid_expressions(method, expression):
    value = {"expression": expression}
    if method == "eoh_json":
        value["thought"] = "Valid description does not widen the grammar."
    with pytest.raises(ValueError, match="finite proposal grammar"):
        parse_response(json.dumps(value), method)
