"""Finite one-action counterfactuals with fixed Best Fit completion."""

import argparse
from collections import Counter
from pathlib import Path

from .artifacts import file_hash, snapshot_source, source_manifest, write_json
from .benchmark import (
    check_certificate,
    make_suite,
    reference_pack,
    reference_scores,
    successful,
    suite_record,
)


def actions(item, remaining):
    return [i for i, space in enumerate(remaining) if space >= item] or [len(remaining)]


def best_fit(item, remaining):
    return min(
        actions(item, remaining),
        key=lambda i: (remaining[i], i) if i < len(remaining) else (float("inf"), i),
    )


def place(item, remaining, chosen, capacity):
    if chosen not in actions(item, remaining):
        raise ValueError("illegal host action")
    if chosen == len(remaining):
        remaining.append(capacity)
    remaining[chosen] -= item


def completion(instance, prefix, remaining, chosen):
    remaining = list(remaining)
    assignments = list(prefix)
    start = len(prefix)
    for offset, item in enumerate(instance.items[start:]):
        selected = chosen if offset == 0 else best_fit(item, remaining)
        place(item, remaining, selected, instance.capacity)
        assignments.append(selected)
    return check_certificate(instance, assignments), assignments


def trace(instance, hindsight=False):
    remaining, prefix, states = [], [], []
    for step, item in enumerate(instance.items):
        default = best_fit(item, remaining)
        outcomes = [
            (a, *completion(instance, prefix, remaining, a)) for a in actions(item, remaining)
        ]
        chosen, bins, certificate = min(outcomes, key=lambda x: (x[1], x[0] != default, x[0]))
        default_bins = next(x[1] for x in outcomes if x[0] == default)
        states.append(
            {
                "step": step,
                "item": item,
                "remaining": list(remaining),
                "default_action": default,
                "best_action": chosen,
                "default_completion_bins": default_bins,
                "best_completion_bins": bins,
                "improvement": default_bins - bins,
                "action_bins": [{"action": a, "bins": b} for a, b, _ in outcomes],
                "best_certificate": certificate,
            }
        )
        selected = chosen if hindsight else default
        place(item, remaining, selected, instance.capacity)
        prefix.append(selected)
    return {
        "instance_id": instance.instance_id,
        "family": instance.family,
        "bins": check_certificate(instance, prefix),
        "assignments": prefix,
        "states": states,
    }


def audit():
    suite = make_suite("train", 12)
    refs = reference_scores(suite)
    baseline, rollout = [], []
    for instance in suite:
        row = trace(instance)
        assert (row["bins"], row["assignments"]) == reference_pack("best_fit", instance)
        baseline.append(row)
        rollout.append(trace(instance, hindsight=True))
    family = Counter()
    for row in rollout:
        family[row["family"]] += row["bins"]
    result = {"total_bins": sum(family.values()), "family_bins": dict(family)}
    return {
        "scope": "training hindsight diagnosis; no eligible online candidate",
        "model_calls": 0,
        "train": suite_record("train", 12),
        "references": refs,
        "best_fit_traces": baseline,
        "hindsight_traces": rollout,
        "hindsight_result": result,
        "hindsight_arithmetic_screen": successful(result, refs),
        "improvable_best_fit_states": sum(
            s["improvement"] > 0 for r in baseline for s in r["states"]
        ),
        "single_deviation_total": sum(
            min(s["best_completion_bins"] for s in r["states"]) for r in baseline
        ),
        "decision_states": sum(len(r["states"]) for r in baseline + rollout),
        "completion_count": sum(
            len(s["action_bins"]) for r in baseline + rollout for s in r["states"]
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path.cwd()
    source = source_manifest(root)
    snapshot_source(root, source, args.output / "source.zip")
    protocol = root / "docs/phase4-decision-v1-protocol.md"
    (args.output / "protocol.md").write_bytes(protocol.read_bytes())
    report = audit()
    for path, expected in source["files"].items():
        if file_hash(root / path) != expected:
            raise ValueError("source changed during execution")
    if file_hash(protocol) != file_hash(args.output / "protocol.md"):
        raise ValueError("protocol changed during execution")
    write_json(args.output / "report.json", report)
    write_json(
        args.output / "manifest.json",
        {
            "status": "completed",
            "source": source,
            "files": {
                n: file_hash(args.output / n) for n in ("source.zip", "protocol.md", "report.json")
            },
        },
    )
    print(
        {
            k: report[k]
            for k in (
                "hindsight_result",
                "hindsight_arithmetic_screen",
                "improvable_best_fit_states",
                "single_deviation_total",
                "decision_states",
                "completion_count",
            )
        }
    )


if __name__ == "__main__":
    main()
