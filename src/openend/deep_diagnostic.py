"""Fixed-budget deeper grammar search, training-only and replayable."""

import argparse
import json
import random
from pathlib import Path

from .artifacts import canonical, digest, file_hash, snapshot_source, source_manifest, write_json
from .benchmark import evaluate, make_suite, pack, reference_scores, successful, suite_record
from .experiment import verify_artifacts
from .policy import ARITY, FEATURES, Policy

CONFIG = {
    "version": "representation-deep-v2",
    "seed": 20261013,
    "attempts": 4096,
    "per_family": 12,
    "split": "train",
}


def proposals():
    rng = random.Random(CONFIG["seed"])
    leaves = [*FEATURES, -2, -1, -0.5, 0, 0.5, 1, 2]

    def tree(depth, force=False):
        if depth == 0 or (not force and rng.random() < 0.30):
            return rng.choice(leaves)
        op = rng.choice(list(ARITY))
        return [op, *(tree(depth - 1) for _ in range(ARITY[op]))]

    for i in range(CONFIG["attempts"]):
        expression = tree(4, True) if i % 2 == 0 else ["add", ["neg", "gap"], tree(3, True)]
        yield Policy.from_object({"expression": expression}).to_object()


def improved(score, baseline):
    return score["total_bins"] < baseline["total_bins"] and all(
        score["family_bins"][name] <= 1.05 * bins for name, bins in baseline["family_bins"].items()
    )


def summary(rows, references):
    # A lower-total earlier policy can violate the family constraint. When stopping
    # on a witness, retain that eligible witness rather than an ineligible candidate.
    best = (
        rows[-1]
        if rows[-1]["improved"]
        else min(rows, key=lambda row: (row["score"]["total_bins"], row["index"]))
    )
    return {
        "attempts": len(rows),
        "unique_policies": len({digest(r["policy"]) for r in rows}),
        "stop_reason": "training_witness" if rows[-1]["improved"] else "attempt_limit",
        "best": best,
        "references": references,
        "utility_successes": sum(r["utility_success"] for r in rows),
        "model_calls": 0,
        "scope": "sampled grammar, training-only",
    }


def run(output, root):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    train = make_suite("train", CONFIG["per_family"])
    refs = reference_scores(train)
    baseline = min(refs.values(), key=lambda r: r["total_bins"])
    plan = list(proposals())
    write_json(output / "plan.json", plan)
    write_json(output / "train.json", suite_record("train", CONFIG["per_family"]))
    (output / "protocol.md").write_bytes(
        (Path(root) / "docs/representation-v2-protocol.md").read_bytes()
    )
    source = source_manifest(root)
    snapshot_source(root, source, output / "source.zip")
    manifest = {
        "experiment_kind": CONFIG["version"],
        "config": CONFIG,
        "source": source,
        "status": "running",
        "input_files": {p.name: file_hash(p) for p in output.iterdir()},
    }
    write_json(output / "run_manifest.json", manifest)
    rows = []
    try:
        with (output / "events.jsonl").open("x", encoding="utf-8") as journal:
            for i, value in enumerate(plan):
                score = evaluate(Policy.from_object(value), train)
                row = {
                    "index": i,
                    "policy": value,
                    "score": score,
                    "improved": improved(score, baseline),
                    "utility_success": successful(score, refs),
                }
                rows.append(row)
                journal.write(canonical(row) + "\n")
                journal.flush()
                if i % 128 == 0:
                    print(
                        f"attempt={i + 1} best_bins={min(r['score']['total_bins'] for r in rows)}",
                        flush=True,
                    )
                if row["improved"]:
                    break
        result = summary(rows, refs)
        winner = Policy.from_object(result["best"]["policy"])
        write_json(
            output / "certificates.json",
            [
                {"instance_id": instance.instance_id, "bins": bins, "assignments": assignments}
                for instance in train
                for bins, assignments in [pack(winner, instance)]
            ],
        )
        write_json(output / "summary.json", result)
        manifest["status"] = "completed"
    except BaseException:
        manifest["status"] = "interrupted_or_failed"
        raise
    finally:
        manifest["output_files"] = {
            p.name: file_hash(p)
            for p in output.iterdir()
            if p.name not in {*manifest["input_files"], "run_manifest.json"}
        }
        write_json(output / "run_manifest.json", manifest)
    return result


def replay(output):
    output = Path(output)
    verify_artifacts(output)
    manifest = json.loads((output / "run_manifest.json").read_text())
    if manifest["status"] != "completed" or manifest["config"] != CONFIG:
        raise ValueError("not a completed v2 diagnostic")
    plan = list(proposals())
    if json.loads((output / "plan.json").read_text()) != plan:
        raise ValueError("proposal plan mismatch")
    if digest(json.loads((output / "train.json").read_text())) != digest(suite_record("train", 12)):
        raise ValueError("training data mismatch")
    train = make_suite("train", 12)
    refs = reference_scores(train)
    baseline = min(refs.values(), key=lambda r: r["total_bins"])
    rows = [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines()]
    if not rows or len(rows) > len(plan):
        raise ValueError("invalid attempt count")
    for i, row in enumerate(rows):
        score = evaluate(Policy.from_object(plan[i]), train)
        expected = {
            "index": i,
            "policy": plan[i],
            "score": score,
            "improved": improved(score, baseline),
            "utility_success": successful(score, refs),
        }
        if row != expected or (i < len(rows) - 1 and row["improved"]):
            raise ValueError("score or early-stop mismatch")
    if not rows[-1]["improved"] and len(rows) != len(plan):
        raise ValueError("premature stop")
    result = summary(rows, refs)
    if result != json.loads((output / "summary.json").read_text()):
        raise ValueError("summary mismatch")
    winner = Policy.from_object(result["best"]["policy"])
    expected = [
        {"instance_id": instance.instance_id, "bins": bins, "assignments": assignments}
        for instance in train
        for bins, assignments in [pack(winner, instance)]
    ]
    if expected != json.loads((output / "certificates.json").read_text()):
        raise ValueError("packing certificate mismatch")
    return {"replay": "matched", "attempts": len(rows), "model_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "replay"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = run(args.output, Path.cwd()) if args.command == "run" else replay(args.output)
    if "best" in result:
        result = {k: v for k, v in result.items() if k not in ("best", "references")} | {
            "best_bins": result["best"]["score"]["total_bins"],
            "best_policy": result["best"]["policy"],
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
