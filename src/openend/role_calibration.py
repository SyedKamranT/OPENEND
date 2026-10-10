"""Fixed training-only critic calibration, separate from coordinator v1."""

import argparse
import json
from pathlib import Path

from .artifacts import canonical, file_hash, snapshot_source, source_manifest, write_json
from .backends import SYSTEM_PROMPT
from .benchmark import Instance, evaluate, make_suite, reference_scores, successful, suite_record
from .experiment import verify_artifacts
from .grammar import policy_schema
from .local import LocalBackend
from .policy import Policy

STATES = [
    {"item": 10, "remaining": [70, 10, 40]},
    {"item": 30, "remaining": [80, 60, 35]},
    {"item": 20, "remaining": [20, 70, 45]},
]
# Independently hand-derived labels and choices, not model adjudications.
CASES = [
    {
        "id": "zero_product",
        "expression": ["mul", "gap", "exact_fit"],
        "label": "first_fit",
        "choices": [0, 0, 0],
    },
    {
        "id": "negative_remaining",
        "expression": ["neg", "remaining"],
        "label": "best_fit",
        "choices": [1, 2, 0],
    },
    {"id": "positive_gap", "expression": "gap", "label": "worst_fit", "choices": [0, 0, 1]},
]
BASE = """Critique the supplied online bin-packing scoring policy. Return only the required JSON.
reference_class describes the ORIGINAL policy: first_fit, best_fit, worst_fit or other.
original_choices and revision_choices predict zero-based selected bin indices for the three
supplied states in order. revision is an executable expression intended to improve packing.
Do not claim novelty. No prose fields are required. A revision may preserve the policy if appropriate.
Expression syntax: feature string, numeric constant, or operator array. Allowed features:
gap, remaining, item, index, fraction, exact_fit. Operators: add, sub, mul, div, min, max
(two operands); abs, neg (one operand). Use at most four operator levels and 31 nodes.
Allowed constants: -2, -1, -0.5, 0, 0.5, 1, 2.
"""
CONTRACT = SYSTEM_PROMPT.split("The host places", 1)[1].split("Improve the given parent", 1)[0]
CONTRACT = "The host places" + CONTRACT
CONFIG = {
    "version": "critic-calibration-v1",
    "model": "qwen3.5:4b",
    "calls": 6,
    "token_ceiling": 20000,
    "max_output_tokens": 384,
    "purpose": "training_only_contract_ablation",
    "acceptance": "full_contract: 3/3 correct original classifications and choice vectors, valid revisions and correct revision choice vectors; complete accounted run",
}


def schema():
    grammar = policy_schema()
    choices = {"type": "array", "items": {"enum": [0, 1, 2]}, "minItems": 3, "maxItems": 3}
    fields = {
        "reference_class": {"enum": ["first_fit", "best_fit", "worst_fit", "other"]},
        "original_choices": choices,
        "revision_choices": choices,
        "revision": grammar["properties"]["expression"],
    }
    return {
        "type": "object",
        "properties": fields,
        "required": list(fields),
        "additionalProperties": False,
        "$defs": grammar["$defs"],
    }


def requests():
    for index, case in enumerate(CASES):
        # Counterbalance order; seed is paired across contract conditions.
        arms = ("minimal", "full_contract") if index % 2 == 0 else ("full_contract", "minimal")
        for arm in arms:
            yield {
                "case_id": case["id"],
                "arm": arm,
                "seed": 16001 + index,
                "system": BASE + (CONTRACT if arm == "full_contract" else ""),
                "prompt": canonical(
                    {
                        "policy": {"expression": case["expression"]},
                        "states": STATES,
                        "capacity": 100,
                    }
                ),
                "schema": schema(),
            }


def assess(text, case, train):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate field")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=unique)
        if not isinstance(value, dict) or set(value) != set(schema()["required"]):
            raise ValueError("invalid fields")
        if value["reference_class"] not in schema()["properties"]["reference_class"]["enum"]:
            raise ValueError("invalid class")
        for name in ("original_choices", "revision_choices"):
            if (
                not isinstance(value[name], list)
                or len(value[name]) != 3
                or any(type(x) is not int or x not in (0, 1, 2) for x in value[name])
            ):
                raise ValueError("invalid choices")
        revision = Policy.from_object({"expression": value["revision"]})
    except (ValueError, TypeError, RecursionError):
        return {"valid": False}
    actual = [revision.choose(s["item"], s["remaining"], 100) for s in STATES]
    score = evaluate(revision, train)
    return {
        "valid": True,
        "classification_correct": value["reference_class"] == case["label"],
        "original_predictions_correct": value["original_choices"] == case["choices"],
        "revision_predictions_correct": value["revision_choices"] == actual,
        "revision_actual_choices": actual,
        "behavior_changed_on_cases": actual != case["choices"],
        "revision": revision.to_object(),
        "training": score,
        "training_utility_success": successful(score, reference_scores(train), 0.01),
    }


def summarize(events):
    result = {}
    for arm in ("minimal", "full_contract"):
        rows = [e for e in events if e["request"]["arm"] == arm]
        metrics = (
            "valid",
            "classification_correct",
            "original_predictions_correct",
            "revision_predictions_correct",
            "behavior_changed_on_cases",
            "training_utility_success",
        )
        result[arm] = {
            name: sum(e["assessment"].get(name, False) for e in rows) for name in metrics
        }
        result[arm]["calls"] = len(rows)
    complete = len(events) == 6 and all(e["status"] == "ok" and e["usage"] for e in events)
    result["accepted"] = complete and all(
        result["full_contract"][k] == 3
        for k in (
            "valid",
            "classification_correct",
            "original_predictions_correct",
            "revision_predictions_correct",
        )
    )
    result["tokens"] = sum(e["usage"].get("total_tokens", 0) for e in events)
    result["complete"] = complete
    return result


def run(output, backend, root):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    train = make_suite("train", 12)
    source = source_manifest(root)
    snapshot_source(root, source, output / "source.zip")
    write_json(output / "train.json", suite_record("train", 12))
    write_json(output / "cases.json", {"cases": CASES, "states": STATES})
    write_json(output / "requests.json", list(requests()))
    manifest = {
        "status": "running",
        "experiment_kind": "critic-calibration-v1",
        "config": CONFIG,
        "source": source,
        "backend": backend.identity(),
        "input_files": {p.name: file_hash(p) for p in output.iterdir()},
    }
    write_json(output / "run_manifest.json", manifest)
    events, spent = [], 0
    write_json(output / "events.json", events)
    with (output / "events.jsonl").open("x", encoding="utf-8") as journal:
        for request in requests():
            reserve = (
                len((request["system"] + request["prompt"]).encode())
                + 512
                + CONFIG["max_output_tokens"]
            )
            if spent + reserve > CONFIG["token_ceiling"]:
                break
            journal.write(canonical({"phase": "request_started", "request": request}) + "\n")
            journal.flush()
            response = backend.generate(
                request["system"], request["prompt"], request["schema"], request["seed"]
            )
            case = next(c for c in CASES if c["id"] == request["case_id"])
            spent += response.usage.get("total_tokens", 0)
            status = (
                "missing_usage"
                if not response.usage
                else "budget_overrun"
                if spent > CONFIG["token_ceiling"]
                else response.status
            )
            event = {
                "request": request,
                "response": response.text,
                "usage": response.usage,
                "metadata": response.metadata,
                "status": status,
                "assessment": assess(response.text, case, train)
                if status == "ok"
                else {"valid": False},
            }
            events.append(event)
            journal.write(canonical({"phase": "response_processed", **event}) + "\n")
            journal.flush()
            write_json(output / "events.json", events)
            print(request["case_id"], request["arm"], status, flush=True)
            if status in ("api_error", "missing_usage", "model_changed", "budget_overrun"):
                break
    summary = summarize(events)
    write_json(output / "summary.json", summary)
    manifest["status"] = "completed" if summary["complete"] else "incomplete"
    manifest["output_files"] = {
        name: file_hash(output / name) for name in ("events.json", "events.jsonl", "summary.json")
    }
    write_json(output / "run_manifest.json", manifest)
    return summary


def replay(output):
    output = Path(output)
    verify_artifacts(output)
    events = json.loads((output / "events.json").read_text())
    if len(events) > CONFIG["calls"] or json.loads((output / "cases.json").read_text()) != {
        "cases": CASES,
        "states": STATES,
    }:
        raise ValueError("calibration case/count mismatch")
    data = json.loads((output / "train.json").read_text())
    train = tuple(Instance(**{**x, "items": tuple(x["items"])}) for x in data["instances"])
    journal = [json.loads(x) for x in (output / "events.jsonl").read_text().splitlines()]
    if len(journal) != 2 * len(events):
        raise ValueError("unresolved journal request")
    for i, (expected, event) in enumerate(zip(requests(), events, strict=False)):
        if (
            event["request"] != expected
            or journal[2 * i] != {"phase": "request_started", "request": expected}
            or journal[2 * i + 1] != {"phase": "response_processed", **event}
        ):
            raise ValueError("request/journal mismatch")
        case = next(c for c in CASES if c["id"] == expected["case_id"])
        actual = (
            assess(event["response"], case, train) if event["status"] == "ok" else {"valid": False}
        )
        if actual != event["assessment"]:
            raise ValueError("assessment mismatch")
    if summarize(events) != json.loads((output / "summary.json").read_text()):
        raise ValueError("summary mismatch")
    return {"replay": "matched", "calls": len(events), "model_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "replay"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = (
        run(
            args.output,
            LocalBackend(CONFIG["model"], CONFIG["max_output_tokens"], structured=True),
            Path.cwd(),
        )
        if args.command == "run"
        else replay(args.output)
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
