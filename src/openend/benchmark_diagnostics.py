"""Fixed-policy, training-only benchmark sensitivity diagnostics."""

import argparse
import itertools
import json
import random
from pathlib import Path

from .artifacts import digest, file_hash
from .benchmark import evaluate, make_suite, reference_scores, successful, suite_record
from .benchmark_acceptance import probe_coverage
from .policy import REFERENCES, Policy
from .search import PROBES, descriptor, distance, signature, sparsity

SEEDS = (2026101501, 2026101502, 2026101503)


def policies():
    return {
        **REFERENCES,
        "exact_fit": Policy.from_object({"expression": "exact_fit"}),
        "index": Policy.from_object({"expression": "index"}),
        "historical_witness": Policy.from_object(
            {
                "expression": [
                    "add",
                    ["neg", "gap"],
                    ["max", ["mul", "item", ["sub", "remaining", "gap"]], "gap"],
                ]
            }
        ),
        "historical_rewrite": Policy.from_object(
            {"expression": ["max", ["sub", ["mul", "item", "item"], "gap"], 0]}
        ),
    }


def stress_panel(seed):
    rng = random.Random(seed)
    result = []
    for kind in ("ordinary", "exact", "mixed"):
        for _ in range(32):
            if kind == "ordinary":
                item = rng.randint(5, 45)
                spaces = [rng.randint(46, 99) for _ in range(6)]
            else:
                item = rng.randint(20, 80)
                spaces = [rng.randint(1, 99) for _ in range(6)]
                spaces[0] = item if kind == "exact" else item - 1
                spaces[1] = rng.randint(item, 99)
            rng.shuffle(spaces)
            result.append((item, tuple(spaces)))
    return tuple(result)


def panel_report(panel, candidates):
    signatures = {name: signature(p, panel) for name, p in candidates.items()}
    groups = {}
    for name, sig in signatures.items():
        groups.setdefault(sig, []).append(name)
    return {
        "panel": panel,
        "sha256": digest(panel),
        "coverage": probe_coverage(panel),
        "policies": {
            name: {
                "signature": sig,
                "reference_distance": sparsity(sig, panel),
                "descriptor": descriptor(sig, panel),
                "cell": [min(5, int(x * 6)) for x in descriptor(sig, panel)],
            }
            for name, sig in signatures.items()
        },
        "collision_groups": [names for names in groups.values() if len(names) > 1],
        "pairwise_disagreement": [
            {"left": a, "right": b, "distance": distance(signatures[a], signatures[b])}
            for a, b in itertools.combinations(candidates, 2)
        ],
    }


def audit():
    candidates = policies()
    train = make_suite("train", 12)
    refs = reference_scores(train)
    best_ref = min(refs, key=lambda name: refs[name]["total_bins"])
    required_bins = 99 * refs[best_ref]["total_bins"] // 100
    scores = {}
    for name, policy in candidates.items():
        score = evaluate(policy, train)
        scores[name] = {
            "evaluation": score,
            "screen_passed": successful(score, refs),
            "bins_above_total_screen": max(0, score["total_bins"] - required_bins),
        }
    panels = {"legacy": panel_report(PROBES, candidates)}
    panels.update({str(seed): panel_report(stress_panel(seed), candidates) for seed in SEEDS})
    return {
        "version": "benchmark-diagnostics-v1",
        "scope": "reused_training_and_public_stress_states",
        "model_calls": 0,
        "policies": {name: p.to_object() for name, p in candidates.items()},
        "train": suite_record("train", 12),
        "reference_scores": refs,
        "best_reference": best_ref,
        "required_total_bins": required_bins,
        "training_results": scores,
        "panels": panels,
        "useful_signal_established_by_fixed_candidates": any(
            s["screen_passed"] for s in scores.values()
        ),
        "limitation": "Finite fixed policies; no full-grammar impossibility or generalization inference.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path.cwd()
    paths = ["docs/phase3-diagnostics-v1-protocol.md"] + [
        f"src/openend/{name}.py"
        for name in (
            "benchmark_diagnostics",
            "benchmark",
            "benchmark_acceptance",
            "policy",
            "search",
            "artifacts",
        )
    ]
    hashes = {}
    for name in paths:
        target = args.output / "snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / name).read_bytes())
        hashes[name] = file_hash(target)
    report = audit()
    for name, expected in hashes.items():
        if file_hash(root / name) != expected:
            raise ValueError("diagnostic source changed during execution")
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "manifest.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "inputs": hashes,
                "report_sha256": file_hash(args.output / "report.json"),
            },
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps(
            {
                "required_bins": report["required_total_bins"],
                "training_bins": {
                    name: value["evaluation"]["total_bins"]
                    for name, value in report["training_results"].items()
                },
                "useful_signal": report["useful_signal_established_by_fixed_candidates"],
            }
        )
    )


if __name__ == "__main__":
    main()
