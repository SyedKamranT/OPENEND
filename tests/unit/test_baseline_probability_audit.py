from pathlib import Path

import pytest

from openend.baseline_probability_audit import audit


def test_pinned_numerical_audit_exposes_scale_and_checks_length_probabilities():
    pytest.importorskip("scipy")
    report = audit(Path(__file__).resolve().parents[2])
    assert len(report["probability_cases"]) == 48
    assert all(r["max_abs_difference"] < 1e-12 for r in report["length_cases"])
    scale = report["score_scale_witness"]
    assert scale["total_bins"][-1] > 0.99
    assert scale["mean_bins"][-1] < 0.5
    assert scale["mean_bins"] == pytest.approx(scale["total_with_scaled_temperature"])
    assert max(r["max_abs_difference"] for r in report["probability_cases"]) > 1e-6
