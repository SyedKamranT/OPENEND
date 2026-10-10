from collections import Counter

from openend.benchmark import make_suite
from openend.policy import REFERENCES
from openend.probe_audit import training_panel


def test_candidate_probes_are_reachable_training_states_and_balanced():
    rows = training_panel()
    assert rows == training_panel()
    assert len(rows) == 64
    assert set(Counter((r["family"], r["exact_fit"]) for r in rows).values()) == {8}
    suite = {instance.instance_id: instance for instance in make_suite("train", 12)}
    for row in rows:
        assert row["instance_id"].startswith("train/")
        instance = suite[row["instance_id"]]
        policy = REFERENCES[row["reference"]]
        remaining = []
        for item in instance.items[: row["step"]]:
            index = policy.choose(item, remaining, instance.capacity)
            if index == len(remaining):
                remaining.append(instance.capacity)
            remaining[index] -= item
        assert remaining == row["remaining"]
        assert row["item"] == instance.items[row["step"]]
        assert sum(space >= row["item"] for space in remaining) >= 2
