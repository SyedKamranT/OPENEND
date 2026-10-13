import io
import json

import pytest

from openend import evidence
from openend.agents import cell_for
from openend.backends import Proposal
from openend.benchmark import make_suite, reference_pack
from openend.coordinator import replay as coordinator_replay
from openend.coordinator import run_condition, run_study
from openend.grounded_calibration import replay, run
from openend.policy import REFERENCES
from openend.probes import build_panel_record, panel_from_record
from openend.research_diagnostics import TARGET_PANEL, assess_target, expressions, target_requests
from tests.integration.test_coordinator import CORPUS, ROOT, ScriptedBackend, config


class GroundedBackend(ScriptedBackend):
    context = 32768

    def __init__(self, false_claim=False):
        super().__init__()
        self.false_claim = false_claim

    def generate(self, system, prompt, output_format, seed):
        self.requests.append((system, prompt, output_format, seed))
        data = json.loads(prompt)
        if output_format == evidence.schema():
            traces = data.get("traces", data.get("behavior_evidence"))
            value = {
                "revision": 0,
                "original_choices": [x["selected_bin"] for x in traces],
                "revision_choices": [0, 0, 0],
            }
            if self.false_claim:
                value["revision_choices"] = [1, 1, 1]
        elif "target_cell" in data:
            value = next(
                p.to_object()
                for p in REFERENCES.values()
                if list(cell_for(p, TARGET_PANEL, 6)) == data["target_cell"]
            )
        else:
            value = {"expression": 0}
        return Proposal(json.dumps(value), {"total_tokens": 40}, {"model": "fake@fixture"})


def test_trace_matches_independent_references_and_certificates():
    for name, policy in REFERENCES.items():
        for instance in make_suite("train", 1):
            result = evidence.training_trace(policy, instance)
            bins, assignments = reference_pack(name, instance)
            assert result["bins"] == bins
            assert result["assignments"] == assignments
    tied = evidence.trace(REFERENCES["first_fit"], 20, [10, 30, 30])
    assert tied["selected_bin"] == 1 and tied["bins"][0]["score"] is None
    assert evidence.trace(REFERENCES["best_fit"], 20, [10])["opens_bin"]
    with pytest.raises(ValueError):
        evidence.training_trace(REFERENCES["best_fit"], make_suite("test", 1)[0])


@pytest.mark.parametrize(
    "change",
    [
        {"original_choices": [1, 0, 0]},
        {"revision_choices": [True, 0, 0]},
        {"novelty": "new discovery"},
        {"revision_choices": [0, 0, 1]},
    ],
)
def test_unsupported_or_malformed_claims_are_rejected(change):
    value = {"revision": 0, "original_choices": [0, 0, 0], "revision_choices": [0, 0, 0]}
    value.update(change)
    result = evidence.assess(json.dumps(value), REFERENCES["first_fit"], make_suite("train", 1))
    assert not result["accepted"] and not result.get("feedback")


def test_rejected_feedback_cannot_reach_recombiner():
    cfg = {**config(), "version": "coordinator-grounded-v2"}
    backend = GroundedBackend(false_claim=True)
    panel = panel_from_record(build_panel_record(cfg, ROOT))
    result = run_condition(
        cfg,
        backend,
        42,
        "coordinator_uniform",
        make_suite("train", 1),
        panel,
        CORPUS,
        io.StringIO(),
    )
    assert len(backend.requests) == 6
    assert [e["status"] for e in result["events"]].count("rejected_critique") == 2
    assert result["tokens_accounted"] == 240
    for event in result["events"]:
        if event["role"] == "recombiner":
            assert json.loads(event["request"]["prompt"])["critique"] is None


def test_grounded_coordinator_replays(tmp_path):
    cfg = {**config(), "version": "coordinator-grounded-v2"}
    output = tmp_path / "coordinator"
    status, _ = run_study(cfg, GroundedBackend(), output, ROOT)
    assert status == "completed"
    assert coordinator_replay(output)["role_calls_recomputed"] == 24


def test_separate_calibration_gates_replay(tmp_path):
    output = tmp_path / "calibration"
    result = run(output, GroundedBackend(false_claim=True), ROOT)
    assert result["complete"]
    assert not result["groups"]["grounded"]["gate_passed"]
    assert result["groups"]["target_only"]["gate_passed"]
    assert replay(output)["calls"] == 9


def test_target_controls_and_representation_scope():
    tasks = list(target_requests())
    assert len(tasks) == 6
    for request in tasks:
        assert ("reachable_witness" in request["payload"]) == (request["arm"] == "witness_control")
        witness = REFERENCES[request["case_id"]]
        assert assess_target(json.dumps(witness.to_object()), request)["target_hit"]
    assert len(list(expressions())) == 1053
