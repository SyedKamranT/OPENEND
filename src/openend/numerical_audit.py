"""Exact-rational sensitivity audit; does not change production float semantics."""

import argparse
import json
from fractions import Fraction
from pathlib import Path

from .artifacts import file_hash, snapshot_source, source_manifest, write_json
from .benchmark import evaluate, make_suite, pack
from .experiment import verify_artifacts
from .policy import Policy


def exact_score(node, features):
    if type(node) in (int, float):
        return Fraction(str(node))
    if isinstance(node, str):
        return features[node]
    op = node[0]
    a = exact_score(node[1], features)
    if op == "abs":
        result = abs(a)
    elif op == "neg":
        result = -a
    else:
        b = exact_score(node[2], features)
        if op == "add":
            result = a + b
        elif op == "sub":
            result = a - b
        elif op == "mul":
            result = a * b
        elif op == "div":
            result = a / b if abs(b) >= Fraction(1, 1000000) else Fraction(0)
        elif op == "min":
            result = min(a, b)
        elif op == "max":
            result = max(a, b)
        else:
            raise ValueError("unknown operator")
    return max(Fraction(-1000000), min(Fraction(1000000), result))


class ExactPolicy:
    def __init__(self, expression):
        self.expression = Policy.from_object({"expression": expression}).to_object()["expression"]

    def choose(self, item, remaining, capacity):
        feasible = [i for i, space in enumerate(remaining) if space >= item]
        if not feasible:
            return len(remaining)

        def score(i):
            space = remaining[i]
            return exact_score(
                self.expression,
                {
                    "gap": Fraction(space - item, capacity),
                    "remaining": Fraction(space, capacity),
                    "item": Fraction(item, capacity),
                    "index": Fraction(i, max(1, len(remaining) - 1)),
                    "fraction": Fraction(item, space),
                    "exact_fit": Fraction(space == item),
                },
            )

        return max(feasible, key=lambda i: (score(i), -i))


def audit(expression):
    train = make_suite("train", 12)
    original, exact = Policy.from_object({"expression": expression}), ExactPolicy(expression)
    original_score, exact_result = evaluate(original, train), evaluate(exact, train)
    divergences = []
    for instance in train:
        remaining = []
        for step, item in enumerate(instance.items):
            selected = original.choose(item, remaining, instance.capacity)
            alternative = exact.choose(item, remaining, instance.capacity)
            if selected != alternative:
                divergences.append(
                    {
                        "instance_id": instance.instance_id,
                        "step": step,
                        "item": item,
                        "remaining": remaining.copy(),
                        "float_choice": selected,
                        "exact_choice": alternative,
                    }
                )
                break
            if selected == len(remaining):
                remaining.append(instance.capacity)
            remaining[selected] -= item
    return {
        "policy": original.to_object(),
        "float": original_score,
        "exact": exact_result,
        "first_divergences": divergences,
        "exact_certificates": [
            {"instance_id": x.instance_id, "bins": bins, "assignments": assignments}
            for x in train
            for bins, assignments in [pack(exact, x)]
        ],
        "scope": "post-hoc training-only numerical diagnostic, not a new search",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    verify_artifacts(args.source)
    saved = json.loads((args.source / "summary.json").read_text())
    expression = saved["best"]["policy"]["expression"]
    args.output.mkdir(parents=True, exist_ok=False)
    source = source_manifest(Path.cwd())
    snapshot_source(Path.cwd(), source, args.output / "source.zip")
    write_json(args.output / "audit.json", audit(expression))
    write_json(
        args.output / "run_manifest.json",
        {
            "status": "completed",
            "experiment_kind": "numerical-audit-v1",
            "source": source,
            "parent_summary_sha256": file_hash(args.source / "summary.json"),
            "input_files": {},
            "output_files": {p.name: file_hash(p) for p in args.output.iterdir()},
        },
    )
    result = json.loads((args.output / "audit.json").read_text())
    print(
        {
            "float_bins": result["float"]["total_bins"],
            "exact_bins": result["exact"]["total_bins"],
            "streams_with_choice_divergence": len(result["first_divergences"]),
        }
    )


if __name__ == "__main__":
    main()
