"""Deterministic retrieval diagnostics with explicit label provenance and abstention."""

import argparse
import json
from pathlib import Path

from .artifacts import digest, file_hash, write_json
from .corpus import load, search


def evaluate(snapshot, queries):
    corpus = load(snapshot)
    k = queries["top_k"]
    if type(k) is not int or not 1 <= k <= 100:
        raise ValueError("invalid k")
    ids = [q["id"] for q in queries["queries"]]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("empty or duplicate query IDs")
    rows = []
    available = {doc["id"] for doc in corpus["documents"]}
    for q in queries["queries"]:
        gold = q["relevant"]
        if not isinstance(gold, list) or len(set(gold)) != len(gold):
            raise ValueError("invalid relevance labels")
        result = search(snapshot, q["query"], k)
        hits = [x["id"] for x in result["hits"]]
        relevant_ranks = [i + 1 for i, doc in enumerate(hits) if doc in gold]
        rows.append(
            {
                "id": q["id"],
                "query": q["query"],
                "relevant": gold,
                "hits": hits,
                "precision_at_k": len(relevant_ranks) / k,
                "recall_at_k": len(relevant_ranks) / len(gold) if gold else None,
                "reciprocal_rank": 1 / min(relevant_ranks) if relevant_ranks else 0,
                "gold_in_corpus": len(set(gold) & available),
                "abstained": not hits,
                "novelty_verdict": result["novelty_verdict"],
            }
        )
    present = [r for r in rows if r["relevant"]]
    absent = [r for r in rows if not r["relevant"]]
    mean = lambda key: sum(r[key] for r in present) / len(present) if present else None
    return {
        "corpus_sha256": corpus["corpus_sha256"],
        "queries_sha256": digest(queries),
        "independent_labels": queries.get("independent_labels", False),
        "rows": rows,
        "metrics": {
            "answerable_queries": len(present),
            "absent_queries": len(absent),
            "macro_precision_at_k": mean("precision_at_k"),
            "macro_recall_at_k": mean("recall_at_k"),
            "mrr": mean("reciprocal_rank"),
            "gold_coverage": sum(r["gold_in_corpus"] for r in present)
            / sum(len(r["relevant"]) for r in present)
            if present
            else None,
            "absent_query_abstention": sum(r["abstained"] for r in absent) / len(absent)
            if absent
            else None,
        },
        "scope": "Recall is over labeled leads, never the entire literature. Same-author labels "
        "are development diagnostics and cannot close independent retrieval validation.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("queries", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "corpus.json").write_bytes(args.snapshot.read_bytes())
    (args.output / "queries.json").write_bytes(args.queries.read_bytes())
    result = evaluate(args.snapshot, json.loads(args.queries.read_text()))
    write_json(args.output / "evaluation.json", result)
    write_json(
        args.output / "run_manifest.json",
        {
            "status": "completed",
            "experiment_kind": "retrieval-development-v2",
            "input_files": {},
            "output_files": {p.name: file_hash(p) for p in args.output.iterdir()},
        },
    )
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
