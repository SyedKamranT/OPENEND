import json
from pathlib import Path

import pytest

from openend import block_runner
from openend.artifacts import digest
from openend.benchmark import pack, reference_pack
from openend.development_blocks import record, suite
from openend.policy import REFERENCES

ROOT = Path(__file__).resolve().parents[2]


def test_block_role_domains_and_stream_prefix_stability():
    seen = set()
    for block in range(3):
        for role in ("train", "development_eval"):
            data = suite(20261014, block, role, 1)
            assert data == suite(20261014, block, role, 1)
            larger = {i.instance_id: i for i in suite(20261014, block, role, 2)}
            for instance in data:
                assert larger[instance.instance_id] == instance
                fingerprint = digest(instance.items)
                assert fingerprint not in seen
                seen.add(fingerprint)
                assert len(instance.items) == 60
                for name, policy in REFERENCES.items():
                    assert pack(policy, instance) == reference_pack(name, instance)
            assert (
                record(20261014, block, role, 1)["scope"] == "public_development_not_confirmation"
            )
    with pytest.raises(ValueError):
        suite(20261014, 0, "confirmatory")


def test_searches_finish_and_selection_is_written_before_evaluation(tmp_path, monkeypatch):
    plan = {
        "master_seed": 17,
        "blocks": 2,
        "search": {**block_runner.PLAN["search"], "calls": 3, "per_family": 1},
    }
    original = block_runner.evaluation
    output = tmp_path / "blocks"

    def checked(plan, blocks):
        assert len(blocks) == 2 and all(r["complete"] for runs in blocks for r in runs)
        frozen = json.loads((output / "selected.json").read_text())
        assert frozen["policies"] == block_runner.selections(blocks)
        assert frozen["sha256"] == digest(frozen["policies"])
        return original(plan, blocks)

    monkeypatch.setattr(block_runner, "evaluation", checked)
    result = block_runner.run(output, ROOT, plan)
    assert result["blocks"] == 2 and result["paired_runs"] == 4
    assert block_runner.replay(output) == {"replay": "matched", "attempts": 24, "model_calls": 0}
