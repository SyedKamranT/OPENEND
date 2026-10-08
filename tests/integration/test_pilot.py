import json
import zipfile
from pathlib import Path

import pytest

from openend.backends import OfflineBackend, Proposal
from openend.experiment import load_config, replay_study, run_study, verify_artifacts

ROOT = Path(__file__).resolve().parents[2]


def config():
    value = load_config(ROOT / "configs/pilot.json")
    value.update(seeds=[42, 137], candidates_per_arm=4, per_family=1)
    return value


def test_offline_experiment_is_reproducible_and_integrity_checked(tmp_path):
    cfg = config()
    first, second = tmp_path / "first", tmp_path / "second"
    status, a = run_study(cfg, OfflineBackend(), first, ROOT)
    _, b = run_study(cfg, OfflineBackend(), second, ROOT)
    assert status == "completed"
    assert a == b
    assert json.loads((first / "runs.json").read_text()) == json.loads(
        (second / "runs.json").read_text()
    )
    assert verify_artifacts(first)["hashes_verified"] > 5
    assert replay_study(first)["replay"] == "matched"
    with zipfile.ZipFile(first / "source.zip") as snapshot:
        assert "src/openend/benchmark.py" in snapshot.namelist()
        assert not any(Path(name).name == ".env" for name in snapshot.namelist())
    events = [json.loads(line) for line in (first / "events.jsonl").read_text().splitlines()]
    assert len(events) == 16
    assert all("audit" not in e and "test/" not in e["prompt"] for e in events)
    runs = json.loads((first / "runs.json").read_text())
    assert all(r["summary"]["validated_novel_success_rate"] is None for r in runs)
    with pytest.raises(FileExistsError):
        run_study(cfg, OfflineBackend(), first, ROOT)
    (first / "events.jsonl").write_text("tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_artifacts(first)


class BadBackend(OfflineBackend):
    def propose(self, parent, fitness, rng):
        return Proposal(
            '{"expression":"import os"}',
            {"input_tokens": 5, "output_tokens": 5, "total_tokens": 10},
            {},
        )


def test_invalid_generations_remain_in_denominator(tmp_path):
    status, _ = run_study(config(), BadBackend(), tmp_path / "bad", ROOT)
    assert status == "completed"
    runs = json.loads((tmp_path / "bad/runs.json").read_text())
    assert all(
        r["summary"]["attempts"] == 4 and r["summary"]["valid_candidates"] == 0 for r in runs
    )
    assert all(r["summary"]["selected_test_bins"] is None for r in runs)


class FailureBackend(OfflineBackend):
    def reservation(self, prompt):
        return 100

    def propose(self, parent, fitness, rng):
        return Proposal(None, {}, {"error_type": "ConnectionError"}, "api_error")


def test_api_failure_stops_without_retry_or_silent_exclusion(tmp_path):
    status, analysis = run_study(config(), FailureBackend(), tmp_path / "failure", ROOT)
    assert status == "incomplete_comparison"
    assert all(not pair["eligible_complete_pair"] for pair in analysis["pairs"])
    runs = json.loads((tmp_path / "failure/runs.json").read_text())
    assert all(r["summary"]["attempts"] == 1 and not r["usage_complete"] for r in runs)


def test_shared_budget_stops_before_call_and_does_not_invent_zero_rate(tmp_path):
    cfg = config()
    cfg["total_tokens_per_arm"] = 1
    status, _ = run_study(cfg, FailureBackend(), tmp_path / "limit", ROOT)
    assert status == "incomplete_comparison"
    runs = json.loads((tmp_path / "limit/runs.json").read_text())
    assert all(r["summary"]["attempts"] == 0 for r in runs)
    assert all(r["summary"]["utility_success_rate"] is None for r in runs)
