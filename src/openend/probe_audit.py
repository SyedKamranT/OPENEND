"""Prepare a training-only candidate probe panel; never changes active search probes."""

import argparse
import random
from collections import defaultdict
from pathlib import Path

from .artifacts import digest, write_json
from .benchmark import FAMILIES, make_suite
from .policy import REFERENCES, Policy
from .search import PROBES, signature


def training_panel():
    buckets = defaultdict(dict)
    for instance in make_suite("train", 12):
        for name, policy in REFERENCES.items():
            remaining = []
            for step, item in enumerate(instance.items):
                feasible = sum(space >= item for space in remaining)
                exact = item in remaining
                # Retain actual choices; forced placements do not distinguish scorers.
                if feasible >= 2 and (not exact or any(space > item for space in remaining)):
                    key = (item, tuple(remaining))
                    buckets[instance.family, exact].setdefault(
                        key,
                        {
                            "item": item,
                            "remaining": remaining.copy(),
                            "capacity": instance.capacity,
                            "instance_id": instance.instance_id,
                            "step": step,
                            "reference": name,
                            "family": instance.family,
                            "exact_fit": exact,
                        },
                    )
                index = policy.choose(item, remaining, instance.capacity)
                if index == len(remaining):
                    remaining.append(instance.capacity)
                remaining[index] -= item
    rng = random.Random(11007)
    rows = []
    for family in FAMILIES:
        for exact in (False, True):
            pool = list(buckets[family, exact].values())
            if len(pool) < 8:
                raise ValueError("insufficient training states for a declared stratum")
            rows.extend(rng.sample(pool, 8))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = training_panel()
    bonus = Policy.from_object({"expression": ["add", "gap", ["mul", 2, "exact_fit"]]})
    worst = REFERENCES["worst_fit"]
    differences = sum(
        bonus.choose(row["item"], row["remaining"], row["capacity"])
        != worst.choose(row["item"], row["remaining"], row["capacity"])
        for row in rows
    )
    data = {
        "version": "training-probes-v3-candidate",
        "status": "diagnostic_only_not_active",
        "sampling_seed": 11007,
        "split": "train",
        "rows": rows,
        "sha256": digest(rows),
        "audit": {
            "count": len(rows),
            "exact_fit_cases": sum(row["exact_fit"] for row in rows),
            "mixed_feasibility_cases": sum(
                any(space < row["item"] for space in row["remaining"]) for row in rows
            ),
            "old_exact_fit_cases": sum(item in remaining for item, remaining in PROBES),
            "counterexample_old_signatures_equal": signature(bonus) == signature(worst),
            "counterexample_new_decision_differences": differences,
        },
        "limitation": "Reference-rollout training panel, not a novelty corpus or a tested treatment improvement.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    write_json(args.output, data)
    print(data["audit"])


if __name__ == "__main__":
    main()
