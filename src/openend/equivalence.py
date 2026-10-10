"""Conservative complete-domain equivalence certificates for index-free policies.

This checks equivalence to three frozen implemented references, not global novelty.
For capacity 100 and integer items, all feasible (item, remaining) pairs are finite.
Index-free scorers assign each feasible bin a score depending only on those pairs.
Constant, strictly descending, or strictly ascending scores therefore reproduce
first-, best-, or worst-fit, including the host's stable earliest-bin tie rule.
"""

import argparse
import json
from itertools import pairwise
from pathlib import Path

from .artifacts import digest, file_hash, write_json
from .experiment import verify_artifacts
from .policy import REFERENCES, Policy, _score


def _uses_index(node):
    if isinstance(node, list):
        return any(_uses_index(child) for child in node[1:])
    return node == "index"


def certify(policy):
    expression = policy.to_object()["expression"]
    base = {
        "policy_sha256": policy.identity,
        "reference_set": {name: ref.identity for name, ref in REFERENCES.items()},
        "scope": "capacity 100, positive integer item sizes, feasible integer remaining capacities, host placement/tie rules",
        "global_novelty": "unresolved",
    }
    if _uses_index(expression):
        return {**base, "verdict": "unresolved", "reason": "index-dependent proof not implemented"}
    constant = decreasing = increasing = True
    rows = []
    for item in range(1, 101):
        scores = [
            _score(
                expression,
                {
                    "gap": (space - item) / 100,
                    "remaining": space / 100,
                    "item": item / 100,
                    "index": 0,
                    "fraction": item / space,
                    "exact_fit": float(space == item),
                },
            )
            for space in range(item, 101)
        ]
        constant &= all(left == right for left, right in pairwise(scores))
        decreasing &= all(left > right for left, right in pairwise(scores))
        increasing &= all(left < right for left, right in pairwise(scores))
        rows.append(scores)
    matches = [
        name
        for name, matches in (
            ("first_fit", constant),
            ("best_fit", decreasing),
            ("worst_fit", increasing),
        )
        if matches
    ]
    return {
        **base,
        "verdict": "known_reference_equivalent" if matches else "unresolved",
        "matches": matches,
        "states_checked": sum(map(len, rows)),
        "score_table_sha256": digest(rows),
        "method": "exhaustive per-item score ordering under the actual bounded interpreter",
        "limitation": "A sufficient equivalence certificate only; no match does not imply novelty. Interpreter correctness is a shared dependency.",
    }


def audit_run(run_path, output):
    run_path, output = Path(run_path), Path(output)
    verify_artifacts(run_path)
    policies = {}
    runs = json.loads((run_path / "runs.json").read_text(encoding="utf-8"))
    for run in runs:
        for event in run["events"]:
            if event["status"] == "ok":
                policy = Policy.from_object(event["policy"])
                policies[policy.identity] = policy
    certificates = {key: certify(policy) for key, policy in sorted(policies.items())}
    result = {
        "version": "reference-equivalence-v1",
        "verifier_sha256": file_hash(Path(__file__)),
        "interpreter_sha256": file_hash(Path(__file__).with_name("policy.py")),
        "run": run_path.as_posix(),
        "run_manifest_sha256": digest(
            json.loads((run_path / "run_manifest.json").read_text(encoding="utf-8"))
        ),
        "purpose": "posthoc verifier diagnostic; original experiment labels remain unchanged",
        "unique_policies": len(policies),
        "certified_reference_equivalents": sum(
            c["verdict"] == "known_reference_equivalent" for c in certificates.values()
        ),
        "certificates": certificates,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    write_json(output, result)
    return {key: value for key, value in result.items() if key != "certificates"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit_run(args.run, args.output), indent=2))


if __name__ == "__main__":
    main()
