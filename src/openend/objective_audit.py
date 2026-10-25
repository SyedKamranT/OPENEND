"""Find and re-evaluate an objective-ranking reversal in preserved training evidence."""

import argparse
import json
from pathlib import Path

from .artifacts import file_hash, write_json
from .benchmark import evaluate, make_suite
from .experiment import verify_artifacts
from .policy import Policy


def audit(source, output):
    source, output = Path(source), Path(output)
    verify_artifacts(source)
    rows = [json.loads(line) for line in (source / "events.jsonl").read_text().splitlines()]
    candidates = [r for r in rows if "score" in r and "policy" in r]
    pair = None
    ordered = sorted(candidates, key=lambda r: (r["score"]["total_bins"], r["index"]))
    for low in ordered:
        higher = next(
            (
                r
                for r in ordered
                if r["score"]["total_bins"] > low["score"]["total_bins"]
                and r["score"]["fitness"] > low["score"]["fitness"]
            ),
            None,
        )
        if higher is not None:
            pair = [low, higher]
            break
    if pair is None:
        raise ValueError("no reversal found in saved training evidence")
    train = make_suite("train", 12)
    for row in pair:
        if evaluate(Policy.from_object(row["policy"]), train) != row["score"]:
            raise ValueError("saved score mismatch")
    result = {
        "status": "training_ranking_reversal_recomputed",
        "model_calls": 0,
        "source_events_sha256": file_hash(source / "events.jsonl"),
        "examples": [
            {
                "index": r["index"],
                "policy": r["policy"],
                "total_bins": r["score"]["total_bins"],
                "fitness": r["score"]["fitness"],
            }
            for r in pair
        ],
        "scope": "Post-hoc objective diagnostic on existing development data, not a new adaptive search.",
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "audit.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.source, args.output), indent=2))


if __name__ == "__main__":
    main()
