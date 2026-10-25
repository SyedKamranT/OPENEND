"""Bounded training diagnosis of coordinated, interpreted scoring sketches."""

import argparse
import json
from pathlib import Path

from .artifacts import file_hash, snapshot_source, source_manifest, write_json
from .benchmark import check_certificate, evaluate, make_suite, pack, reference_scores, successful
from .benchmark_diagnostics import SEEDS, policies, stress_panel
from .grammar import validate_proposal_policy
from .policy import Policy
from .search import PROBES, signature, sparsity


def plan():
    rows = []
    targets = [0.1, 0.2, 0.3, 0.4, 0.5] + [["mul", c, "item"] for c in (0.5, 1, 2)]
    for t in targets:
        expressions = [
            ("residual", None, ["neg", ["abs", ["sub", "gap", t]]]),
            ("plateau", None, ["max", ["neg", "gap"], ["neg", t]]),
        ] + [
            ("triangle", w, ["sub", ["mul", w, ["min", "gap", ["sub", t, "gap"]]], "gap"])
            for w in (0, 0.5, 1, 2, 4, 8)
        ]
        for family, weight, expression in expressions:
            rows.append(
                {
                    "kind": "sketch",
                    "family": family,
                    "target": t,
                    "weight": weight,
                    "expression": expression,
                }
            )
    controls = {
        k: p
        for k, p in policies().items()
        if k in ("first_fit", "best_fit", "worst_fit", "historical_witness")
    }
    controls["posthoc_bridge"] = Policy.from_object({"expression": ["max", "gap", "fraction"]})
    rows.extend(
        {"kind": "control", "family": k, "expression": p.to_object()["expression"]}
        for k, p in controls.items()
    )
    return rows


def trace_effect(policy, traces):
    counts = {"beneficial": 0, "harmful": 0, "neutral_deviations": 0, "corrected_opportunities": 0}
    opportunities = []
    for row in traces:
        for state in row["states"]:
            action = policy.choose(state["item"], state["remaining"], 100)
            bins = next(x["bins"] for x in state["action_bins"] if x["action"] == action)
            delta = state["default_completion_bins"] - bins
            if delta > 0:
                counts["beneficial"] += 1
            elif delta < 0:
                counts["harmful"] += 1
            elif action != state["default_action"]:
                counts["neutral_deviations"] += 1
            if state["improvement"] > 0:
                counts["corrected_opportunities"] += delta > 0
                opportunities.append(
                    {
                        "instance_id": row["instance_id"],
                        "step": state["step"],
                        "action": action,
                        "completion_gain": delta,
                    }
                )
    return dict(**counts, opportunities=opportunities)


def audit(rows, traces):
    suite = make_suite("train", 12)
    refs = reference_scores(suite)
    panels = {"legacy": PROBES, **{str(s): stress_panel(s) for s in SEEDS}}
    results = []
    for index, row in enumerate(rows):
        p = Policy.from_object({"expression": row["expression"]})
        try:
            validate_proposal_policy(p)
            eligible = True
        except ValueError:
            eligible = False
        score = evaluate(p, suite)
        certificates = []
        for instance, scored in zip(suite, score["instances"]):
            bins, assignments = pack(p, instance)
            assert check_certificate(instance, assignments) == bins == scored["bins"]
            certificates.append({"instance_id": instance.instance_id, "assignments": assignments})
        results.append(
            dict(
                index=index,
                **row,
                proposal_eligible=eligible,
                score=score,
                gain_over_incumbent=1475 - score["total_bins"],
                screen_passed=successful(score, refs),
                trace_effect=trace_effect(p, traces),
                certificates=certificates,
                distances={k: sparsity(signature(p, panel), panel) for k, panel in panels.items()},
            )
        )
    sketches = [r for r in results if r["kind"] == "sketch"]
    return {
        "scope": "adaptive training-only sketch census",
        "results": results,
        "summary": {
            "attempts": len(sketches),
            "controls": len(results) - len(sketches),
            "eligible": sum(r["proposal_eligible"] for r in sketches),
            "best_bins": min(r["score"]["total_bins"] for r in sketches),
            "screen_passes": sum(r["screen_passed"] for r in sketches),
            "best_index": min(sketches, key=lambda r: r["score"]["total_bins"])["index"],
            "max_opportunities": max(
                r["trace_effect"]["corrected_opportunities"] for r in sketches
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = source_manifest(Path.cwd())
    snapshot_source(Path.cwd(), source, args.output / "source.zip")
    protocol = Path("docs/coordinated-sketch-v1-protocol.md")
    (args.output / "protocol.md").write_bytes(protocol.read_bytes())
    input_path = Path("results/raw/phase4-decision-v1/report.json")
    input_hash = file_hash(input_path)
    original = json.loads(input_path.read_text())
    manifest = json.loads(input_path.with_name("manifest.json").read_text())
    assert input_hash == manifest["files"]["report.json"]
    rows = plan()
    write_json(args.output / "plan.json", rows)
    report = audit(rows, original["best_fit_traces"])
    assert file_hash(input_path) == input_hash
    assert all(file_hash(Path(p)) == h for p, h in source["files"].items())
    assert file_hash(protocol) == file_hash(args.output / "protocol.md")
    write_json(args.output / "report.json", report)
    write_json(
        args.output / "manifest.json",
        {
            "source": source,
            "input_sha256": input_hash,
            "files": {
                p: file_hash(args.output / p)
                for p in ("source.zip", "protocol.md", "plan.json", "report.json")
            },
        },
    )
    print(report["summary"])


if __name__ == "__main__":
    main()
