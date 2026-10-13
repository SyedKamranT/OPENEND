"""Training-only finite representation audit and separate target calibration tasks."""

import argparse
import json
from pathlib import Path

from .agents import POLICY_SYSTEM, cell_for
from .artifacts import digest, file_hash, snapshot_source, source_manifest, write_json
from .benchmark import evaluate, make_suite, reference_scores, successful, suite_record
from .experiment import verify_artifacts
from .grammar import policy_schema
from .policy import FEATURES, REFERENCES, Policy
from .role_calibration import STATES
from .search import descriptor, signature


def expressions():
    """Exhaust this declared sublanguage, not the complete bounded grammar."""
    leaves = [*FEATURES, -2, -1, -0.5, 0, 0.5, 1, 2]
    yield from leaves
    for op in ("neg", "abs"):
        for leaf in leaves:
            yield [op, leaf]
    for op in ("add", "sub", "mul", "div", "min", "max"):
        for left in leaves:
            for right in leaves:
                yield [op, left, right]


def representation_audit():
    train = make_suite("train", 12)
    references = reference_scores(train)
    rows = []
    for expression in expressions():
        policy = Policy.from_object({"expression": expression})
        score = evaluate(policy, train)
        rows.append(
            {
                "policy": policy.to_object(),
                "id": policy.identity,
                "score": score,
                "training_utility_success": successful(score, references),
            }
        )
    best = min(rows, key=lambda row: (row["score"]["total_bins"], row["id"]))
    # This oracle chooses a different policy AFTER seeing each stream. It is not online
    # or deployable, but exposes heterogeneity that a single policy must generalize over.
    oracle_bins = sum(
        min(row["score"]["instances"][i]["bins"] for row in rows) for i in range(len(train))
    )
    return {
        "version": "representation-audit-v1",
        "split": "train",
        "suite": suite_record("train", 12),
        "candidates": rows,
        "candidate_count": len(rows),
        "candidates_sha256": digest(rows),
        "references": references,
        "best": best,
        "per_instance_oracle_bins": oracle_bins,
        "utility_successes": sum(row["training_utility_success"] for row in rows),
        "scope": "Exhaustive only for leaves and one-operator expressions. A failure does "
        "not prove full-grammar impossibility. Oracle selection is non-deployable. "
        "All examples and scores are development data, not confirmation.",
    }


TARGET_PANEL = tuple((state["item"], tuple(state["remaining"])) for state in STATES)
TARGET_SEMANTICS = (
    "Capacity=100. For each supplied state select the feasible bin with largest score; "
    "ties choose the lowest index. x=mean((remaining[choice]-item)/100). "
    "y=mean(choice/max(1,len(remaining)-1)). Cell=(min(5,floor(6*x)), "
    "min(5,floor(6*y))). Compute means over ALL three states. "
    "Reach the requested cell; packing utility is not this calibration's objective."
)


def target_requests():
    for i, (name, witness) in enumerate(REFERENCES.items()):
        for arm in ("target_only", "witness_control"):
            payload = {
                "states": STATES,
                "descriptor_semantics": TARGET_SEMANTICS,
                "target_cell": list(cell_for(witness, TARGET_PANEL, 6)),
            }
            if arm == "witness_control":
                payload["reachable_witness"] = witness.to_object()
            yield {
                "kind": "target",
                "case_id": name,
                "arm": arm,
                "seed": 26001 + i,
                "system": POLICY_SYSTEM + "\nFor this task prioritize the target cell only.",
                "payload": payload,
                "schema": policy_schema(),
            }


def assess_target(text, request):
    try:
        policy = Policy.from_text(text)
    except ValueError:
        return {"valid": False, "target_hit": False}
    sig = signature(policy, TARGET_PANEL)
    cell = list(cell_for(policy, TARGET_PANEL, 6))
    return {
        "valid": True,
        "policy": policy.to_object(),
        "choices": list(sig),
        "descriptor": list(descriptor(sig, TARGET_PANEL)),
        "cell": cell,
        "target_hit": cell == request["payload"]["target_cell"],
        "scope": "three-state controllability only; no utility or full-panel claim",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.replay:
        verify_artifacts(args.output)
        saved = json.loads((args.output / "representation.json").read_text())
        if digest(saved) != digest(representation_audit()):
            raise ValueError("representation audit replay mismatch")
        print({"replay": "matched", "candidates": saved["candidate_count"], "model_calls": 0})
        return
    args.output.mkdir(parents=True, exist_ok=False)
    source = source_manifest(Path.cwd())
    snapshot_source(Path.cwd(), source, args.output / "source.zip")
    result = representation_audit()
    write_json(args.output / "representation.json", result)
    write_json(
        args.output / "run_manifest.json",
        {
            "experiment_kind": "representation-audit-v1",
            "status": "completed",
            "source": source,
            "input_files": {},
            "output_files": {p.name: file_hash(p) for p in args.output.iterdir()},
        },
    )
    print(
        {
            "candidates": result["candidate_count"],
            "best_train_bins": result["best"]["score"]["total_bins"],
            "oracle_train_bins": result["per_instance_oracle_bins"],
            "utility_successes": result["utility_successes"],
        }
    )


if __name__ == "__main__":
    main()
