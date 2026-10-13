"""Executable, bounded critic evidence. Model prose is never trusted feedback."""

import json

from .benchmark import check_certificate, evaluate
from .grammar import policy_schema
from .policy import Policy, _score
from .role_calibration import BASE, CONTRACT, STATES

SYSTEM = (
    BASE
    + CONTRACT
    + """
You receive host-computed traces of the ORIGINAL policy. Use these observations.
Return only revision, original_choices, revision_choices. Each choices array has three
zero-based bin indices for states in order. The host checks every prediction and rejects
the entire feedback if any prediction is false. Predict the revision by executing its
score semantics; copying the original trace is insufficient. No novelty or utility claims.
"""
)
# BASE contains the old classification instructions; remove that contract for this version.
SYSTEM = SYSTEM.replace(
    "reference_class describes the ORIGINAL policy: first_fit, best_fit, worst_fit or other.\n", ""
)


def schema():
    grammar = policy_schema()
    fields = {
        "revision": grammar["properties"]["expression"],
        "original_choices": {
            "type": "array",
            "items": {"enum": [0, 1, 2]},
            "minItems": 3,
            "maxItems": 3,
        },
        "revision_choices": {
            "type": "array",
            "items": {"enum": [0, 1, 2]},
            "minItems": 3,
            "maxItems": 3,
        },
    }
    return {
        "type": "object",
        "properties": fields,
        "required": list(fields),
        "additionalProperties": False,
        "$defs": grammar["$defs"],
    }


def trace(policy, item, remaining, capacity=100):
    if (
        type(capacity) is not int
        or capacity < 1
        or type(item) is not int
        or not 1 <= item <= capacity
        or not isinstance(remaining, (tuple, list))
        or any(type(x) is not int or not 0 <= x <= capacity for x in remaining)
    ):
        raise ValueError("invalid trace state")
    rows = []
    expression = policy.to_object()["expression"]
    for i, space in enumerate(remaining):
        if space < item:
            rows.append({"bin": i, "feasible": False, "score": None})
            continue
        features = {
            "gap": (space - item) / capacity,
            "remaining": space / capacity,
            "item": item / capacity,
            "index": i / max(1, len(remaining) - 1),
            "fraction": item / space,
            "exact_fit": float(space == item),
        }
        rows.append(
            {
                "bin": i,
                "feasible": True,
                "features": features,
                "score": _score(expression, features),
            }
        )
    feasible = [row for row in rows if row["feasible"]]
    choice = (
        max(feasible, key=lambda row: (row["score"], -row["bin"]))["bin"]
        if feasible
        else len(remaining)
    )
    if choice != policy.choose(item, remaining, capacity):
        raise ValueError("trace disagrees with policy interpreter")
    return {
        "item": item,
        "remaining": list(remaining),
        "capacity": capacity,
        "bins": rows,
        "selected_bin": choice,
        "opens_bin": not feasible,
        "tie_break": "earliest feasible bin with maximal score",
    }


def behavior_evidence(policy):
    return [trace(policy, **state) for state in STATES]


def training_trace(policy, instance):
    if not instance.instance_id.startswith("train/"):
        raise ValueError("critic traces must be training-only")
    remaining, assignments, steps = [], [], []
    for item in instance.items:
        step = trace(policy, item, remaining, instance.capacity)
        choice = step["selected_bin"]
        steps.append(step)
        assignments.append(choice)
        if choice == len(remaining):
            remaining.append(instance.capacity)
        remaining[choice] -= item
    return {
        "instance_id": instance.instance_id,
        "steps": steps,
        "assignments": assignments,
        "bins": check_certificate(instance, assignments),
    }


def assess(text, original, train):
    """Accept only exactly checked statements; retain rejections for audit."""
    if not train or any(not x.instance_id.startswith("train/") for x in train):
        raise ValueError("feedback evaluation must be training-only")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate field")
            result[key] = value
        return result

    try:
        if not isinstance(text, str) or len(text.encode()) > 16384:
            raise ValueError("oversized feedback")
        value = json.loads(text, object_pairs_hook=unique)
        if not isinstance(value, dict) or set(value) != set(schema()["required"]):
            raise ValueError("invalid fields")
        for key in ("original_choices", "revision_choices"):
            if (
                not isinstance(value[key], list)
                or len(value[key]) != 3
                or any(type(x) is not int or x not in (0, 1, 2) for x in value[key])
            ):
                raise ValueError("invalid choices")
        revision = Policy.from_object({"expression": value["revision"]})
    except (ValueError, TypeError, RecursionError):
        return {"valid": False, "accepted": False, "reason": "invalid_schema_or_policy"}
    before, after = behavior_evidence(original), behavior_evidence(revision)
    original_ok = value["original_choices"] == [x["selected_bin"] for x in before]
    revision_ok = value["revision_choices"] == [x["selected_bin"] for x in after]
    old_score, new_score = evaluate(original, train), evaluate(revision, train)
    accepted = original_ok and revision_ok
    return {
        "valid": True,
        "accepted": accepted,
        "reason": "verified_on_fixed_states" if accepted else "unsupported_behavior_claim",
        "original_correct": original_ok,
        "revision_correct": revision_ok,
        "revision": revision.to_object(),
        "revision_traces": after,
        "training_bin_delta": new_score["total_bins"] - old_score["total_bins"],
        "training_improved": new_score["total_bins"] < old_score["total_bins"],
        "feedback": {
            "revision": revision.to_object(),
            "verified_traces": after,
            "training_bin_delta": new_score["total_bins"] - old_score["total_bins"],
            "scope": "fixed-state behavior and training measurement only; novelty unresolved",
        }
        if accepted
        else None,
    }
