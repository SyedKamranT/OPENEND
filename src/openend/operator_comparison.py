"""Matched fixed-parent comparison of subtree and single-token proposals."""

import argparse
import random
from pathlib import Path

from .artifacts import canonical, digest, file_hash, snapshot_source, source_manifest, write_json
from .benchmark import evaluate, make_suite, reference_scores, successful
from .benchmark_diagnostics import SEEDS, policies, stress_panel
from .policy import ARITY, FEATURES, mutate
from .search import PROBES, signature, sparsity
from .utility_runner import parse


def conservative_mutate(parent, rng):
    tree = parent.to_object()["expression"]
    nodes = []

    def walk(node, path):
        nodes.append((node, path))
        if isinstance(node, list):
            for i in range(1, len(node)):
                walk(node[i], path + [i])

    walk(tree, [])
    node, path = rng.choice(nodes)
    if isinstance(node, list):
        node[0] = rng.choice(
            [op for op, arity in ARITY.items() if arity == ARITY[node[0]] and op != node[0]]
        )
    else:
        replacement = rng.choice([x for x in [*FEATURES, -2, -1, -0.5, 0, 0.5, 1, 2] if x != node])
        if not path:
            tree = replacement
        else:
            target = tree
            for index in path[:-1]:
                target = target[index]
            target[path[-1]] = replacement
    return canonical({"expression": tree})


def trajectory(score):
    return digest([(x["instance_id"], x["assignment_sha256"]) for x in score["instances"]])


def audit():
    suite = make_suite("train", 12)
    refs = reference_scores(suite)
    parents = {k: v for k, v in policies().items() if k in (*refs, "historical_witness")}
    parent_scores = {k: evaluate(p, suite) for k, p in parents.items()}
    incumbent = min(s["total_bins"] for s in parent_scores.values())
    panels = {"legacy": PROBES, **{str(seed): stress_panel(seed) for seed in SEEDS}}
    ceilings = {
        key: max(sparsity(signature(p, panel), panel) for p in parents.values())
        for key, panel in panels.items()
    }
    cache, events, summary = {}, [], {}
    for op, function in (("subtree", mutate), ("single_token", conservative_mutate)):
        rows = []
        for name, parent in parents.items():
            seen = set()
            for seed in range(2026102500, 2026102628):
                response = function(parent, random.Random(seed))
                row = {
                    "operator": op,
                    "parent": name,
                    "seed": seed,
                    "response": response,
                    "status": "invalid",
                    "gain": 0,
                }
                try:
                    child = parse(response)
                except ValueError:
                    pass
                else:
                    if child.identity not in cache:
                        score = evaluate(child, suite)
                        distances = {
                            key: sparsity(signature(child, panel), panel)
                            for key, panel in panels.items()
                        }
                        cache[child.identity] = {
                            "score": score,
                            "reference_distances": distances,
                            "trajectory": trajectory(score),
                        }
                    value = cache[child.identity]
                    score = value["score"]
                    reach = {
                        key: d > ceilings[key] for key, d in value["reference_distances"].items()
                    }
                    row.update(
                        status="valid",
                        policy_id=child.identity,
                        **value,
                        gain=max(0, incumbent - score["total_bins"]),
                        parent_gain=max(0, parent_scores[name]["total_bins"] - score["total_bins"]),
                        exact_parent_copy=child.identity == parent.identity,
                        repeated=child.identity in seen,
                        parent_training_agreement=value["trajectory"]
                        == trajectory(parent_scores[name]),
                        reach_by_panel=reach,
                        robust_reach=all(reach.values()),
                        screen_passed=successful(score, refs),
                    )
                    seen.add(child.identity)
                rows.append(row)
        events.extend(rows)
        valid = [r for r in rows if r["status"] == "valid"]
        summary[op] = {
            "attempts": len(rows),
            "valid": len(valid),
            "unique": len({r["policy_id"] for r in valid}),
            "copies": sum(r["exact_parent_copy"] for r in valid),
            "parent_training_agreements": sum(r["parent_training_agreement"] for r in valid),
            "best_bins": min(r["score"]["total_bins"] for r in valid),
            "improved_incumbent": sum(r["gain"] > 0 for r in valid),
            "screen_passes": sum(r["screen_passed"] for r in valid),
            "robust_reach": sum(r["robust_reach"] for r in valid),
            "useful_and_robust": sum(r["robust_reach"] and r["screen_passed"] for r in valid),
            "reach_by_panel": {k: sum(r["reach_by_panel"][k] for r in valid) for k in panels},
        }
    valid = [r for r in events if r["status"] == "valid"]
    passing = [r for r in valid if r["screen_passed"]]
    chosen = min(passing or valid, key=lambda r: r["score"]["total_bins"])
    return {
        "scope": "adaptive training-only operator diagnosis",
        "model_calls": 0,
        "incumbent_bins": incumbent,
        "panel_thresholds": ceilings,
        "summary": summary,
        "events": events,
        "selected": chosen,
        "distinct_evaluations": len(cache),
        "training_ids": [i.instance_id for i in suite],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = source_manifest(Path.cwd())
    snapshot_source(Path.cwd(), source, args.output / "source.zip")
    protocol = Path("docs/operator-comparison-v1-protocol.md")
    (args.output / "protocol.md").write_bytes(protocol.read_bytes())
    report = audit()
    if any(file_hash(Path(p)) != h for p, h in source["files"].items()):
        raise ValueError("source changed")
    if file_hash(protocol) != file_hash(args.output / "protocol.md"):
        raise ValueError("protocol changed")
    write_json(args.output / "report.json", report)
    write_json(
        args.output / "manifest.json",
        {
            "source": source,
            "files": {
                p: file_hash(args.output / p) for p in ("source.zip", "protocol.md", "report.json")
            },
        },
    )
    print(report["summary"])


if __name__ == "__main__":
    main()
