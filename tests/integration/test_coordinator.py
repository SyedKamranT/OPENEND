import io
import json
from pathlib import Path

from openend.agents import CRITIC_SCHEMA, cell_for, target_library
from openend.backends import Proposal
from openend.benchmark import make_suite
from openend.coordinator import load_config, replay, report, run_condition, run_study
from openend.probes import build_panel_record, panel_from_record

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data/corpus/frozen-review-notes-v1.json"


class ScriptedBackend:
    context = 8192

    def __init__(self, bad_critic=False, missing_usage=False):
        self.requests = []
        self.bad_critic = bad_critic
        self.missing_usage = missing_usage

    def identity(self):
        return {
            "kind": "scripted_test",
            "model": "fake",
            "model_digest": "fixture",
            "options": {"num_ctx": self.context},
        }

    def generate(self, system, prompt, output_format, seed):
        self.requests.append((system, prompt, output_format, seed))
        if output_format == CRITIC_SCHEMA:
            value = {
                "weaknesses": ["Known rule"],
                "revision": "Use the donor's gap term.",
                "prior_art_query": "online bin packing",
            }
            if self.bad_critic:
                value["prior_art_query"] = "x" * 161
        else:
            value = {"expression": 0}
        return Proposal(
            json.dumps(value),
            {}
            if self.missing_usage
            else {"input_tokens": 30, "output_tokens": 10, "total_tokens": 40},
            {"model": "fake@fixture"},
        )


def config():
    value = load_config(ROOT / "configs/coordinator_smoke_v1.json")
    value["per_family"] = 1
    return value


def test_coordinator_conditions_charge_all_roles_replay_and_keep_fallback(tmp_path):
    backend = ScriptedBackend()
    output = tmp_path / "study"
    status, runs = run_study(config(), backend, output, ROOT)
    assert status == "completed" and len(backend.requests) == 24
    by_condition = {r["condition"]: r for r in runs}
    assert by_condition["independent"]["summary"]["valid_policies"] == 6
    assert by_condition["retrieval"]["summary"]["valid_policies"] == 6
    for name in ("coordinator_uniform", "coordinator_targeted"):
        summary = by_condition[name]["summary"]
        assert summary["valid_policies"] == 4 and summary["valid_critiques"] == 2
        assert summary["tokens_accounted"] == 240
        assert summary["used_reference_fallback"] is True
        assert summary["outcome"] == "no_training_improvement"
    for system, prompt, _, _ in backend.requests:
        assert "test/" not in prompt and "validation/" not in prompt
        assert "audit" not in json.loads(prompt)
    for event in by_condition["independent"]["events"]:
        assert event["retrieval"] is None and event["target"] is None
    for event in by_condition["coordinator_uniform"]["events"]:
        assert event["target"] is None
    for event in by_condition["coordinator_targeted"]["events"]:
        assert event["target"] is not None
    assert replay(output)["role_calls_recomputed"] == 24
    assert "no_training_improvement" in report(output)


def test_unaccounted_usage_stops_whole_study_without_free_retries(tmp_path):
    backend = ScriptedBackend(missing_usage=True)
    status, runs = run_study(config(), backend, tmp_path / "failure", ROOT)
    assert status == "incomplete_comparison"
    assert len(backend.requests) == 1 and len(runs) == 1
    assert runs[0]["summary"]["outcome"] == "incomplete_comparison"


def test_invalid_critique_consumes_call_without_repair():
    backend = ScriptedBackend(bad_critic=True)
    panel = panel_from_record(build_panel_record(config(), ROOT))
    run = run_condition(
        config(),
        backend,
        42,
        "coordinator_targeted",
        make_suite("train", 1),
        panel,
        CORPUS,
        io.StringIO(),
    )
    assert len(backend.requests) == 6
    assert [e["status"] for e in run["events"]].count("invalid_critique") == 2
    assert run["tokens_accounted"] == 240


def test_budget_admission_makes_no_model_call():
    cfg = config()
    cfg["tokens_per_condition"] = 1
    backend = ScriptedBackend()
    panel = panel_from_record(build_panel_record(cfg, ROOT))
    run = run_condition(
        cfg, backend, 42, "independent", make_suite("train", 1), panel, CORPUS, io.StringIO()
    )
    assert run["stop_reason"] == "token_admission_limit"
    assert backend.requests == [] and run["events"] == []


def test_target_cells_have_reachable_witnesses():
    panel = panel_from_record(build_panel_record(config(), ROOT))
    library = target_library(panel, 6)
    assert len(library) > 3
    for cell, policies in library.items():
        assert policies
        for policy in policies:
            assert cell_for(policy, panel, 6) == cell
