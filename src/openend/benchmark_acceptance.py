"""Deterministic Phase 3 contract checks and descriptor blind-spot witnesses.

Diagnostic fixtures are public development data. No search panel is replaced.
"""

import argparse
import itertools
import json
from pathlib import Path

from .artifacts import digest, file_hash
from .benchmark import Instance, check_certificate, pack, reference_pack
from .development_blocks import record, suite
from .policy import REFERENCES, Policy
from .search import PROBES, signature, sparsity


def probe_coverage(panel):
    return {
        "states": len(panel),
        "exact_fit_states": sum(any(s == item for s in spaces) for item, spaces in panel),
        "mixed_feasibility_states": sum(
            any(s < item for s in spaces) and any(s >= item for s in spaces)
            for item, spaces in panel
        ),
        "no_feasible_bin_states": sum(not any(s >= item for s in spaces) for item, spaces in panel),
        "all_feasible_states": sum(all(s >= item for s in spaces) for item, spaces in panel),
    }


def audit():
    checks = 0
    for items in itertools.product((2, 4, 6, 8), repeat=4):
        instance = Instance("acceptance/tiny", "diagnostic", 10, items)
        for name, policy in REFERENCES.items():
            result = pack(policy, instance)
            if result != reference_pack(name, instance):
                raise ValueError("reference mismatch")
            if check_certificate(instance, result[1]) != result[0]:
                raise ValueError("certificate mismatch")
            checks += 1
    datasets, seen = [], set()
    for block in range(2):
        for role in ("train", "development_eval"):
            instances = suite(20261015, block, role, 1)
            for instance in instances:
                content = digest([instance.capacity, instance.items])
                if content in seen:
                    raise ValueError("duplicate stream in acceptance fixture")
                seen.add(content)
                for name, policy in REFERENCES.items():
                    if pack(policy, instance) != reference_pack(name, instance):
                        raise ValueError("development reference mismatch")
                    checks += 1
            data = record(20261015, block, role, 1)
            datasets.append({"block": block, "role": role, "sha256": data["sha256"]})

    # Same legacy signature, different behavior: exact_fit is zero on all old probes.
    first = REFERENCES["first_fit"]
    exact = Policy.from_object({"expression": "exact_fit"})
    witness = (40, (80, 40))
    contract_cases = [
        {
            "name": "open_when_none_fit",
            "policy": first,
            "item": 60,
            "remaining": (40, 50),
            "expected": 2,
        },
        {"name": "earliest_tie", "policy": first, "item": 40, "remaining": (60, 60), "expected": 0},
        {
            "name": "filter_infeasible",
            "policy": first,
            "item": 40,
            "remaining": (20, 60),
            "expected": 1,
        },
        {
            "name": "exact_fit_eligible",
            "policy": exact,
            "item": 40,
            "remaining": (80, 40),
            "expected": 1,
        },
        {
            "name": "do_not_offer_empty_bin",
            "policy": REFERENCES["worst_fit"],
            "item": 40,
            "remaining": (60,),
            "expected": 0,
        },
    ]
    outcomes = []
    for case in contract_cases:
        choice = case["policy"].choose(case["item"], case["remaining"], 100)
        if choice != case["expected"]:
            raise ValueError(f"contract mismatch: {case['name']}")
        outcomes.append({"name": case["name"], "choice": choice, "passed": True})
    return {
        "version": "benchmark-acceptance-v1",
        "scope": "public development contract checks; not scientific validation",
        "reference_comparisons": checks,
        "distinct_development_streams": len(seen),
        "dataset_records": datasets,
        "host_contract_cases": outcomes,
        "legacy_probe_sha256": digest(PROBES),
        "legacy_probe_coverage": probe_coverage(PROBES),
        "blind_spot_witness": {
            "policies": [first.to_object(), exact.to_object()],
            "legacy_signatures_equal": signature(first) == signature(exact),
            "item": witness[0],
            "remaining": witness[1],
            "choices": [p.choose(*witness, 100) for p in (first, exact)],
        },
        "reference_distances": {name: sparsity(signature(p)) for name, p in REFERENCES.items()},
        "implementation_sha256": file_hash(Path(__file__)),
        "limitations": [
            "Finite fixtures are not proof for all inputs.",
            "No proposal generation, utility improvement or novelty claim is tested.",
            "No legacy search probe, corpus or experimental outcome is changed.",
            "Search descriptors require at least one feasible existing bin; opening cases are host checks.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(f"Verified {result['reference_comparisons']} reference comparisons; saved {args.output}")


if __name__ == "__main__":
    main()
