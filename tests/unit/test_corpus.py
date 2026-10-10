import json
from pathlib import Path

import pytest

from openend.corpus import freeze, load, search

ROOT = Path(__file__).resolve().parents[2]


def notes():
    return json.loads((ROOT / "data/corpus/review-notes-v1.json").read_text())


def test_frozen_corpus_is_deterministic_and_rejects_changes(tmp_path):
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    a = freeze(notes(), first)
    b = freeze(list(reversed(notes())), second)
    assert a["corpus_sha256"] == b["corpus_sha256"]
    assert load(first) == a
    with pytest.raises(FileExistsError):
        freeze(notes(), first)
    modified = json.loads(first.read_text())
    modified["documents"][0]["note"] = "altered evidence"
    first.write_text(json.dumps(modified))
    with pytest.raises(ValueError, match="integrity"):
        load(first)


def test_retrieval_returns_grounded_leads_and_abstains_on_novelty(tmp_path):
    snapshot = tmp_path / "corpus.json"
    freeze(notes(), snapshot)
    result = search(snapshot, "Sodarace walking robots", top_k=1)
    assert result["hits"][0]["id"] == "elm-2022"
    assert result["hits"][0]["source_url"].endswith("2206.08896v1")
    assert result["novelty_verdict"] == "unresolved"
    assert search(snapshot, "unrepresentedtermxyz")["hits"] == []
    assert search(snapshot, "unrepresentedtermxyz")["novelty_verdict"] == "unresolved"
    assert search(snapshot, "")["hits"] == []


def test_duplicate_ids_cannot_mask_documents(tmp_path):
    documents = notes()
    with pytest.raises(ValueError, match="duplicate"):
        freeze(documents + [documents[0]], tmp_path / "bad.json")
