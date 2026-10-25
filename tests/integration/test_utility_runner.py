import io
import json
from pathlib import Path

import pytest

from openend.backends import Proposal
from openend.benchmark import make_suite
from openend.utility_runner import CONFIG, Offline, condition, parse, replay, run

ROOT = Path(__file__).resolve().parents[2]


class Scripted:
    context = 8192

    def __init__(self, mode="ok"):
        self.mode, self.calls = mode, 0

    def identity(self):
        return {
            "kind": "scripted",
            "model": "fixture",
            "model_digest": "fixed",
            "options": {"num_ctx": self.context},
        }

    def generate(self, system, prompt, schema, seed):
        self.calls += 1
        assert "fitness" not in system.lower() and "fitness" not in prompt.lower()
        assert "reference_weighted" not in prompt and "probabilities" not in prompt
        assert "training_total_bins" in prompt
        if self.mode == "exception":
            raise RuntimeError("transport interrupted")
        return Proposal(
            "bad" if self.mode == "invalid" else '{"expression":["neg","gap"]}',
            {} if self.mode == "missing" else {"total_tokens": 100},
            {"model": "wrong" if self.mode == "changed" else "fixture@fixed"},
        )


def config():
    return {**CONFIG, "calls": 6, "seeds": [42], "per_family": 1}


def test_scripted_total_bin_run_replays_every_state(tmp_path):
    backend = Scripted()
    result = run(config(), backend, tmp_path / "run", ROOT)
    assert result["status"] == "completed" and backend.calls == 12
    assert replay(tmp_path / "run") == {"replay": "matched", "attempts": 12, "model_calls": 0}
    assert all(r["selected"]["used_fallback"] for r in result["runs"])


@pytest.mark.parametrize("mode,stop", [("missing", "missing_usage"), ("changed", "model_changed")])
def test_terminal_failures_stop_whole_study_and_replay(tmp_path, mode, stop):
    backend = Scripted(mode)
    result = run(config(), backend, tmp_path / "run", ROOT)
    assert backend.calls == 1 and result["status"] == "incomplete"
    assert result["runs"][0]["stop"] == stop
    assert replay(tmp_path / "run")["attempts"] == 1


def test_invalid_attempts_charge_budget_and_admission_stops_before_request():
    backend = Scripted("invalid")
    result = condition(config(), backend, 42, "uniform", make_suite("train", 1), io.StringIO())
    assert result["valid_policies"] == 0 and result["tokens_accounted"] == 600
    assert result["selected"]["used_fallback"]
    backend = Scripted()
    result = condition(
        {**config(), "tokens": 1}, backend, 42, "uniform", make_suite("train", 1), io.StringIO()
    )
    assert result["stop"] == "token_admission" and backend.calls == 0
    with pytest.raises(ValueError):
        condition(config(), backend, 42, "uniform", make_suite("test", 1), io.StringIO())


def test_exception_preserves_unresolved_request(tmp_path):
    with pytest.raises(RuntimeError):
        run(config(), Scripted("exception"), tmp_path / "run", ROOT)
    manifest = json.loads((tmp_path / "run/run_manifest.json").read_text())
    assert manifest["status"] == "interrupted_or_failed"
    journal = (tmp_path / "run/events.jsonl").read_text().splitlines()
    assert len(journal) == 1 and json.loads(journal[0])["phase"] == "started"


def test_finite_grammar_and_offline_backend(tmp_path):
    for text in (
        '{"expression":9}',
        '{"expression":0,"expression":1}',
        '{"expression":["neg",["neg",["neg",["neg",["neg","gap"]]]]]}',
    ):
        with pytest.raises(ValueError):
            parse(text)
    result = run(config(), Offline(), tmp_path / "run", ROOT)
    assert result["status"] == "completed"
    assert all(r["tokens_accounted"] == 0 for r in result["runs"])
    assert replay(tmp_path / "run")["attempts"] == 12


def test_local_backend_argument_contract_and_incomplete_response(tmp_path):
    class LocalContract(Scripted):
        # Deliberately match LocalBackend's argument name, not the stored schema key.
        def generate(self, system, prompt, output_format, seed):
            assert output_format["required"] == ["expression"]
            response = super().generate(system, prompt, output_format, seed)
            response.status = "incomplete_response"
            return response

    backend = LocalContract()
    output = tmp_path / "local-contract"
    result = run(config(), backend, output, ROOT)
    assert result["status"] == "completed" and backend.calls == 12
    assert all(r["valid_policies"] == 0 and r["tokens_accounted"] == 600 for r in result["runs"])
    assert replay(output)["attempts"] == 12
