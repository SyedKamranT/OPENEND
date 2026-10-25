import json
from pathlib import Path

import pytest

from openend.model_audit_validation import validate

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "docs/independent-review-v1/cases.json"
REVIEW = ROOT / "docs/independent-review-v1/model-audit-gemini-v1.json"
CORPUS = ROOT / "data/corpus/frozen-packing-notes-v2.json"


def test_model_audit_controls_do_not_certify_novelty():
    result = validate(PACKET, REVIEW, CORPUS)
    assert result["packet_traces_replayed"] == 18
    assert len(result["controls"]) == 5
    assert all(r["verdict_agrees"] for r in result["controls"])
    assert sum(r["score_states_checked"] for r in result["controls"]) == 25250
    assert result["unresolved_novelty_cases"] == ["case-02"]
    assert not result["retrieval_evaluation_executed"]
    assert result["human_reviews_completed"] == 0


@pytest.mark.parametrize(
    "field,value", [("packet_sha256", "wrong"), ("independent_attestation", True)]
)
def test_model_audit_rejects_identity_or_independence_change(tmp_path, field, value):
    review = json.loads(REVIEW.read_text())
    review[field] = value
    path = tmp_path / "review.json"
    path.write_text(json.dumps(review))
    with pytest.raises(ValueError):
        validate(PACKET, path, CORPUS)
