"""Run explicitly in the NumPy audit environment; core runtime needs no NumPy."""

import shutil
from pathlib import Path

import pytest

from openend.baseline_evaluator_audit import audit, load_evaluators

pytest.importorskip("numpy")
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def report():
    return audit(ROOT)


def test_native_unused_bin_eligibility_changes_worst_fit(report):
    row = next(
        r
        for r in report["packing_witnesses"]
        if r["items"] == [40, 40, 20] and r["policy"] == "worst_fit"
    )
    assert (row["openend_bins"], row["eoh"], row["funsearch"]) == (1, 3, 3)


def test_reference_controls_and_exact_fits_agree(report):
    for row in report["packing_witnesses"]:
        if row["policy"] in ("first_fit", "best_fit"):
            assert row["openend_bins"] == row["eoh"] == row["funsearch"]


def test_eoh_objective_only_retains_last_dataset(report):
    assert report["eoh_last_dataset_objectives"] == {"a_then_b": 1.0, "b_then_a": 0.0}


def test_funsearch_objective_is_negative_mean_not_total(report):
    assert report["funsearch_negative_mean_bins"] == -1.5
    assert report["openend_total_bins"] == 3


def test_modified_source_is_rejected_before_execution(tmp_path):
    folder = tmp_path / "data/baselines/evaluator-v1"
    shutil.copytree(ROOT / "data/baselines/evaluator-v1", folder)
    source = next(folder.glob("*run.py.txt"))
    source.write_bytes(source.read_bytes() + b"\nraise RuntimeError('must not execute')\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        load_evaluators(tmp_path)
