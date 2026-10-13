"""Generate blinded technical audit material without inventing reviewer judgments."""

import argparse
import json
import random
from pathlib import Path

from .artifacts import digest, write_json
from .corpus import load
from .evidence import behavior_evidence
from .policy import Policy
from .role_calibration import CONTRACT

CASES = [
    ("first_fit_control", 0),
    ("constant_disguise", ["mul", "gap", "exact_fit"]),
    ("best_fit_control", ["neg", "gap"]),
    ("best_fit_disguise", ["div", "item", "remaining"]),
    ("worst_fit_control", "gap"),
    (
        "threshold_training_witness",
        ["add", ["neg", "gap"], ["max", ["mul", "item", ["sub", "remaining", "gap"]], "gap"]],
    ),
]
VERDICTS = {"known_reference", "known_other", "no_equivalent_found_in_scope", "unresolved"}


def build(output, corpus_path):
    output = Path(output)
    if (output / "cases.json").exists():
        raise FileExistsError("packet already exists")
    output.mkdir(parents=True, exist_ok=True)
    corpus = load(corpus_path)
    cases = list(CASES)
    random.Random(20261013).shuffle(cases)
    rows, key = [], {}
    for i, (origin, expression) in enumerate(cases):
        policy = Policy.from_object({"expression": expression})
        case_id = f"case-{i + 1:02}"
        rows.append(
            {"case_id": case_id, "policy": policy.to_object(), "traces": behavior_evidence(policy)}
        )
        key[case_id] = origin
    packet = {
        "version": "independent-review-v1",
        "contract": CONTRACT,
        "corpus_sha256": corpus["corpus_sha256"],
        "cases": rows,
        "scope": "mechanism-review controls and unresolved candidate; not utility claims",
    }
    packet["packet_sha256"] = digest(packet)
    write_json(output / "cases.json", packet)
    write_json(output / "maintainer-key.json", key)
    write_json(
        output / "review-template.json",
        {
            "packet_sha256": packet["packet_sha256"],
            "reviewer_id": None,
            "independent_attestation": None,
            "conflicts": None,
            "completed_date": None,
            "cases": [
                {
                    "case_id": row["case_id"],
                    "verdict": None,
                    "reasoning": None,
                    "source_urls": [],
                    "search_log": [],
                    "search_complete": False,
                }
                for row in rows
            ],
            "retrieval_queries": [],
            "status": "blank_template_not_review_evidence",
        },
    )
    return {"cases": len(rows), "packet_sha256": packet["packet_sha256"], "reviews_completed": 0}


def check_review(packet, review):
    """Check completeness only. An attestation is not authenticated independence."""
    if (
        review.get("packet_sha256") != packet["packet_sha256"]
        or not isinstance(review.get("reviewer_id"), str)
        or not review["reviewer_id"].strip()
        or review.get("independent_attestation") is not True
    ):
        raise ValueError("missing matching packet, reviewer or independence attestation")
    expected = {row["case_id"] for row in packet["cases"]}
    cases = review.get("cases", [])
    if len(cases) != len(expected) or {r["case_id"] for r in cases} != expected:
        raise ValueError("incomplete or duplicate case judgments")
    for row in cases:
        if (
            row.get("verdict") not in VERDICTS
            or not isinstance(row.get("reasoning"), str)
            or not row["reasoning"].strip()
        ):
            raise ValueError("missing verdict or reasoning")
        if row["verdict"].startswith("known") and not row.get("source_urls"):
            raise ValueError("known verdict requires evidence")
        if row["verdict"] == "no_equivalent_found_in_scope" and (
            row.get("search_complete") is not True or not row.get("search_log")
        ):
            raise ValueError("negative search claim requires completed search log")
    return {
        "format_complete": True,
        "independence": "self_attested_not_authenticated",
        "scientific_adjudication": "pending",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--corpus", type=Path, default=Path("data/corpus/frozen-packing-notes-v2.json")
    )
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.corpus), indent=2))


if __name__ == "__main__":
    main()
