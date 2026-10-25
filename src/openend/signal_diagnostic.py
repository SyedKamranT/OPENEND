"""Bounded training-only signal search and certified hindsight headroom."""

import argparse
from collections import Counter
from pathlib import Path

from .artifacts import file_hash, snapshot_source, source_manifest, write_json
from .benchmark import (
    check_certificate,
    evaluate,
    make_suite,
    pack,
    reference_scores,
    successful,
    suite_record,
)
from .policy import Policy
from .utility_runner import parse


def decreasing_certificate(instance, best_fit):
    """Use future item order, then relabel bins by first original-order appearance."""
    loads, assignments = [], [None] * len(instance.items)
    for index in sorted(range(len(instance.items)), key=lambda i: (-instance.items[i], i)):
        item = instance.items[index]
        feasible = [b for b, load in enumerate(loads) if load + item <= instance.capacity]
        if not feasible:
            chosen = len(loads)
            loads.append(0)
        else:
            chosen = max(feasible, key=lambda b: (loads[b], -b)) if best_fit else feasible[0]
        loads[chosen] += item
        assignments[index] = chosen
    labels = {}
    result = [labels.setdefault(b, len(labels)) for b in assignments]
    check_certificate(instance, result)
    return result


def candidates():
    for template in range(4):
        for k in range(21):
            t = k / 20
            tree = (
                ["max", ["sub", t, "gap"], 0],
                ["neg", ["abs", ["sub", "gap", t]]],
                ["sub", ["sub", "exact_fit", "gap"], ["mul", t, "index"]],
                ["add", ["neg", "gap"], ["mul", t, "index"]],
            )[template]
            yield template, t, Policy.from_object({"expression": tree})


def audit():
    suite = make_suite("train", 12)
    refs = reference_scores(suite)
    offline = {}
    for name, best in (("first_fit_decreasing", False), ("best_fit_decreasing", True)):
        rows, families = [], Counter()
        for instance in suite:
            assignments = decreasing_certificate(instance, best)
            bins = check_certificate(instance, assignments)
            families[instance.family] += bins
            rows.append(
                {
                    "instance_id": instance.instance_id,
                    "assignments": assignments,
                    "bins": bins,
                    "lower_bound": instance.lower_bound,
                    "known_optimum": instance.known_optimum,
                }
            )
        result = {"total_bins": sum(families.values()), "family_bins": dict(families)}
        offline[name] = {
            **result,
            "passes_arithmetic_screen": successful(result, refs),
            "eligible_online_policy": False,
            "instances": rows,
        }
    attempts, cache = [], {}
    for template, t, policy in candidates():
        duplicate = policy.identity in cache
        if not duplicate:
            cache[policy.identity] = evaluate(policy, suite)
        score = cache[policy.identity]
        try:
            parse('{"expression":' + policy.expression_json + "}")
            eligible = True
        except ValueError:
            eligible = False
        attempts.append(
            {
                "attempt": len(attempts),
                "template": template,
                "t": t,
                "policy": policy.to_object(),
                "id": policy.identity,
                "duplicate": duplicate,
                "proposal_grammar_eligible": eligible,
                "score": score,
                "screen_passed": successful(score, refs),
            }
        )
    passing = [a for a in attempts if a["screen_passed"]]
    selected = min(passing or attempts, key=lambda a: (a["score"]["total_bins"], a["attempt"]))
    policy = Policy.from_object(selected["policy"])
    certificates = [
        {"instance_id": i.instance_id, "assignments": pack(policy, i)[1]} for i in suite
    ]
    return {
        "scope": "reused training only",
        "model_calls": 0,
        "train": suite_record("train", 12),
        "references": refs,
        "offline_hindsight": offline,
        "attempts": attempts,
        "distinct_policies": len(cache),
        "selected": selected,
        "selected_certificates": certificates,
        "screen_passing_attempts": len(passing),
        "proposal_eligible_passing_attempts": sum(a["proposal_grammar_eligible"] for a in passing),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path.cwd()
    source = source_manifest(root)
    snapshot_source(root, source, args.output / "source.zip")
    protocol = root / "docs/phase4-signal-v1-protocol.md"
    (args.output / "protocol.md").write_bytes(protocol.read_bytes())
    report = audit()
    for relative, expected in source["files"].items():
        if file_hash(root / relative) != expected:
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
                name: file_hash(args.output / name)
                for name in ("source.zip", "protocol.md", "report.json")
            },
        },
    )
    print(
        {
            "attempts": len(report["attempts"]),
            "best_bins": report["selected"]["score"]["total_bins"],
            "passing": report["screen_passing_attempts"],
            "offline_bins": {n: r["total_bins"] for n, r in report["offline_hindsight"].items()},
        }
    )


if __name__ == "__main__":
    main()
