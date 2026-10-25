"""Validate external model audit mechanics without certifying novelty or independence."""

import argparse
import json
from itertools import pairwise
from pathlib import Path

from .artifacts import digest, file_hash, write_json
from .evidence import behavior_evidence, trace
from .policy import Policy


def validate(packet_path, review_path, corpus_path):
    packet = json.loads(Path(packet_path).read_text())
    review = json.loads(Path(review_path).read_text())
    expected_hash = packet["packet_sha256"]
    if digest({k: v for k, v in packet.items() if k != "packet_sha256"}) != expected_hash:
        raise ValueError("packet hash mismatch")
    if review.get("packet_sha256") != expected_hash:
        raise ValueError("review packet mismatch")
    if review.get("independent_attestation") is not False:
        raise ValueError("external model audit must not attest human independence")
    ids = [row["case_id"] for row in packet["cases"]]
    reviewed = [row["case_id"] for row in review["cases"]]
    if sorted(ids) != sorted(reviewed):
        raise ValueError("missing or duplicate cases")
    references = {
        "0": "first_fit",
        '["mul","gap","exact_fit"]': "first_fit",
        '["neg","gap"]': "best_fit",
        '["div","item","remaining"]': "best_fit",
        '"gap"': "worst_fit",
    }
    controls, unresolved, traces = [], [], 0
    for row in packet["cases"]:
        policy = Policy.from_object(row["policy"])
        if behavior_evidence(policy) != row["traces"]:
            raise ValueError("packet trace mismatch")
        traces += len(row["traces"])
        reference = references.get(policy.expression_json)
        if reference is None:
            unresolved.append(row["case_id"])
            continue
        checked = 0
        # All feasible integer residual capacities, for every positive item at C=100.
        # These five expressions do not use index or cross-bin features. Constant or
        # strict monotone ranks imply the reference choice for any feasible list.
        for item in range(1, 101):
            scores = [r["score"] for r in trace(policy, item, list(range(item, 101)))["bins"]]
            if reference == "first_fit":
                matches = all(s == scores[0] for s in scores)
            elif reference == "best_fit":
                matches = all(a > b for a, b in pairwise(scores))
            else:
                matches = all(a < b for a, b in pairwise(scores))
            if not matches:
                raise ValueError("reference rank mismatch")
            checked += len(scores)
        judgment = next(r for r in review["cases"] if r["case_id"] == row["case_id"])
        controls.append(
            {
                "case_id": row["case_id"],
                "reference": reference,
                "score_states_checked": checked,
                "verdict_agrees": judgment["verdict"] == "known_reference",
            }
        )
    corpus = json.loads(Path(corpus_path).read_text())
    if corpus["corpus_sha256"] != packet["corpus_sha256"]:
        raise ValueError("corpus identity mismatch")
    from .corpus import load

    load(corpus_path)
    records = {doc["id"] for doc in corpus["documents"]}
    queries = review.get("retrieval_queries", [])
    query_ids = [q["query_id"] for q in queries]
    if len(query_ids) != len(set(query_ids)):
        raise ValueError("duplicate query IDs")
    for q in queries:
        if not set(q["relevant_record_ids"]).issubset(records):
            raise ValueError("unknown relevance record")
    return {
        "status": "mechanics_checked_scientific_adjudication_pending",
        "input_hashes": {
            Path(p).name: file_hash(p) for p in (packet_path, review_path, corpus_path)
        },
        "packet_traces_replayed": traces,
        "controls": controls,
        "unresolved_novelty_cases": unresolved,
        "scope": "Five reference controls at capacity 100 with positive integer items; not six-case novelty accuracy or literature validation.",
        "retrieval_queries": len(queries),
        "answerable_queries": sum(bool(q["relevant_record_ids"]) for q in queries),
        "absent_queries": sum(not q["relevant_record_ids"] for q in queries),
        "retrieval_labels": "single_model_provisional_not_independent_adjudicated_qrels",
        "retrieval_evaluation_executed": False,
        "human_reviews_completed": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    folder = Path("docs/independent-review-v1")
    result = validate(
        folder / "cases.json",
        folder / "model-audit-gemini-v1.json",
        Path("data/corpus/frozen-packing-notes-v2.json"),
    )
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "validation.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
