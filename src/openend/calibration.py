"""Fixed, training-only grammar calibration; no validation/test access."""

import argparse
import random
from pathlib import Path

from .artifacts import source_manifest, write_json
from .backends import prompt_for
from .benchmark import evaluate, make_suite
from .local import LocalBackend
from .policy import REFERENCES, InvalidPolicy, Policy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    backend = LocalBackend(args.model, 512, structured=True)
    train = make_suite("train", 12)
    manifest = {
        "purpose": "training_only_grammar_calibration",
        "attempts": 6,
        "acceptance": "at least 5/6 valid; no missing usage or transport error",
        "backend": backend.identity(),
        "source": source_manifest(Path.cwd()),
    }
    write_json(args.output / "manifest.json", manifest)
    events = []
    for index, (name, parent) in enumerate(list(REFERENCES.items()) * 2):
        fitness = evaluate(parent, train)["fitness"]
        result = backend.propose(parent, fitness, random.Random(9001 + index))
        event = {
            "attempt": index,
            "parent": name,
            "prompt": prompt_for(parent, fitness),
            "response_text": result.text,
            "usage": result.usage,
            "metadata": result.metadata,
            "status": result.status,
        }
        if result.status == "ok":
            try:
                policy = Policy.from_text(result.text)
                event["train"] = evaluate(policy, train)
            except InvalidPolicy:
                event["status"] = "invalid_policy"
        events.append(event)
        write_json(args.output / "events.json", events)
        print(f"Calibration {index + 1}/6: {event['status']}", flush=True)
    valid = sum(event["status"] == "ok" for event in events)
    accepted = valid >= 5 and all(
        event["status"] not in ("api_error", "missing_usage", "model_changed") for event in events
    )
    write_json(args.output / "summary.json", {"valid": valid, "total": 6, "accepted": accepted})
    if not accepted:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
