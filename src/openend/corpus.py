"""Frozen review-note snapshots and deterministic local lexical retrieval.

These notes are source leads, not complete paper contents or novelty judgments.
"""

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from .artifacts import canonical, digest


def validate_documents(documents):
    fields = {
        "id",
        "title",
        "source_url",
        "source_version",
        "reviewed_date",
        "evidence_scope",
        "note",
    }
    if not isinstance(documents, list) or not documents:
        raise ValueError("a nonempty document list is required")
    identifiers = set()
    for document in documents:
        if (
            not isinstance(document, dict)
            or set(document) != fields
            or any(not isinstance(value, str) or not value.strip() for value in document.values())
        ):
            raise ValueError("invalid document metadata")
        if document["id"] in identifiers:
            raise ValueError("duplicate document id")
        identifiers.add(document["id"])
        url = urlsplit(document["source_url"])
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("source must be a public HTTPS citation without credentials")
    return sorted(documents, key=lambda document: document["id"])


def freeze(documents, output):
    documents = validate_documents(documents)
    payload = {
        "schema_version": 1,
        "scope": "curated_review_notes_only_not_full_text",
        "documents": documents,
        "document_hashes": {document["id"]: digest(document) for document in documents},
    }
    payload["corpus_sha256"] = digest(payload)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, indent=2) + "\n")
    return payload


def load(path):
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    expected = record.pop("corpus_sha256")
    if record.get("schema_version") != 1 or digest(record) != expected:
        raise ValueError("corpus snapshot integrity check failed")
    documents = validate_documents(record["documents"])
    if record["document_hashes"] != {document["id"]: digest(document) for document in documents}:
        raise ValueError("document integrity check failed")
    return {**record, "corpus_sha256": expected}


def search(snapshot, query, top_k=5):
    if type(top_k) is not int or not 1 <= top_k <= 100:
        raise ValueError("top_k must be between 1 and 100")
    record = load(snapshot)
    documents = record["documents"]
    tokenize = lambda text: re.findall(r"[a-z0-9]+", text.lower())
    terms = sorted(set(tokenize(query)))
    bags = [Counter(tokenize(document["title"] + " " + document["note"])) for document in documents]
    lengths = [sum(bag.values()) for bag in bags]
    document_frequencies = Counter(term for bag in bags for term in bag)
    mean_length = sum(lengths) / len(lengths)
    hits = []
    for document, bag, length in zip(documents, bags, lengths):
        score = 0.0
        for term in terms:
            frequency = bag[term]
            if not frequency:
                continue
            containing = document_frequencies[term]
            idf = math.log(1 + (len(bags) - containing + 0.5) / (containing + 0.5))
            score += (
                idf * frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * length / mean_length))
            )
        if score:
            hits.append(
                {
                    **document,
                    "score": score,
                    "document_sha256": record["document_hashes"][document["id"]],
                }
            )
    hits.sort(key=lambda hit: (-hit["score"], hit["id"]))
    return {
        "query": query,
        "corpus_sha256": record["corpus_sha256"],
        "retriever": "lexical-bm25-v1",
        "hits": hits[:top_k],
        "novelty_verdict": "unresolved",
        "limitation": "Matches are research leads; no matches are not evidence of novelty. Recall on independent queries is unmeasured.",
    }


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("freeze")
    build.add_argument("input", type=Path)
    build.add_argument("--output", type=Path, required=True)
    retrieve = commands.add_parser("search")
    retrieve.add_argument("snapshot", type=Path)
    retrieve.add_argument("--query", required=True)
    retrieve.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    if args.command == "freeze":
        record = freeze(json.loads(args.input.read_text(encoding="utf-8")), args.output)
        print(
            canonical(
                {"documents": len(record["documents"]), "corpus_sha256": record["corpus_sha256"]}
            )
        )
    else:
        print(json.dumps(search(args.snapshot, args.query, args.top_k), indent=2))


if __name__ == "__main__":
    main()
