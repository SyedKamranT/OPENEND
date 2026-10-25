"""Common-seed fixed-parent proposal diagnostic; no dynamic search claims."""

import argparse
import random
from pathlib import Path

from .artifacts import file_hash, snapshot_source, source_manifest, write_json
from .benchmark import evaluate, make_suite, reference_scores, successful, suite_record
from .benchmark_diagnostics import policies
from .policy import mutate
from .search import signature, sparsity
from .utility_runner import parse


def retained_gain(score, incumbent):
    return 0 if score is None else max(0, incumbent - score["total_bins"])


def audit():
    suite = make_suite("train", 12)
    refs = reference_scores(suite)
    incumbent = min(x["total_bins"] for x in refs.values())
    parents = {k: v for k, v in policies().items() if k in (*refs, "historical_witness")}
    cache, rows, events = {}, {}, []
    for name, parent in parents.items():
        baseline = evaluate(parent, suite)
        sig = signature(parent)
        own, seen = [], set()
        for seed in range(2026102500, 2026102628):
            response = mutate(parent, random.Random(seed))
            row = {
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
                    cache[child.identity] = evaluate(child, suite)
                score = cache[child.identity]
                row.update(
                    status="valid",
                    policy_id=child.identity,
                    score=score,
                    gain=retained_gain(score, incumbent),
                    parent_improved=score["total_bins"] < baseline["total_bins"],
                    screen_passed=successful(score, refs),
                    parent_probe_agreement=signature(child) == sig,
                    repeated_within_parent=child.identity in seen,
                )
                seen.add(child.identity)
            own.append(row)
        events.extend(own)
        valid = [x for x in own if x["status"] == "valid"]
        rows[name] = {
            "policy": parent.to_object(),
            "baseline_bins": baseline["total_bins"],
            "raw_weight": 0.05 + sparsity(sig),
            "attempts": len(own),
            "valid": len(valid),
            "distinct_valid": len(seen),
            "strict_reference_improvements": sum(x["gain"] > 0 for x in own),
            "parent_improvements": sum(x["parent_improved"] for x in valid),
            "screen_passes": sum(x["screen_passed"] for x in valid),
            "parent_probe_agreements": sum(x["parent_probe_agreement"] for x in valid),
            "mean_retained_gain": sum(x["gain"] for x in own) / len(own),
        }
    total = sum(x["raw_weight"] for x in rows.values())
    for row in rows.values():
        row["weighted_probability"] = row["raw_weight"] / total
    return {
        "scope": "fixed-parent reused-training mutation diagnosis",
        "model_calls": 0,
        "train": suite_record("train", 12),
        "references": refs,
        "parents": rows,
        "events": events,
        "unique_evaluations": len(cache),
        "uniform_expected_gain": sum(x["mean_retained_gain"] for x in rows.values()) / len(rows),
        "weighted_expected_gain": sum(
            x["mean_retained_gain"] * x["weighted_probability"] for x in rows.values()
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = source_manifest(Path.cwd())
    snapshot_source(Path.cwd(), source, args.output / "source.zip")
    protocol = Path("docs/parent-opportunity-v1-protocol.md")
    (args.output / "protocol.md").write_bytes(protocol.read_bytes())
    report = audit()
    if any(file_hash(Path(n)) != h for n, h in source["files"].items()):
        raise ValueError("source changed during run")
    if file_hash(protocol) != file_hash(args.output / "protocol.md"):
        raise ValueError("protocol changed during run")
    write_json(args.output / "report.json", report)
    write_json(
        args.output / "manifest.json",
        {
            "source": source,
            "files": {
                n: file_hash(args.output / n) for n in ("source.zip", "protocol.md", "report.json")
            },
        },
    )
    print({k: v for k, v in report.items() if k not in ("events", "train", "references")})


if __name__ == "__main__":
    main()
