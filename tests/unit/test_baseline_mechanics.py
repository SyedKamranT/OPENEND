"""Differential tests against hash-pinned, reviewed upstream functions only."""

import __future__

import ast
import heapq
import json
import random
from pathlib import Path

import pytest

from openend.artifacts import file_hash
from openend.baseline_mechanics import (
    eoh_parents,
    eoh_survivors,
    funsearch_length_probabilities,
    funsearch_reduced_score,
    funsearch_scores,
    funsearch_signature,
    funsearch_temperature,
)

ROOT = Path(__file__).resolve().parents[2] / "data/baselines/upstream-v1"
PINS = {
    "FeiLiu36/EoH": "4b2338fc2317c743cec50c5c7a2e4684707af973",
    "google-deepmind/funsearch": "cc53f274237d7ab05c19df939edbc1f9616a7c19",
}


def upstream(path, name, namespace=None):
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8-sig"))
    record = next(row for row in manifest["files"] if row["upstream_path"] == path)
    assert record["commit"] == PINS[record["repo"]]
    local = ROOT / record["local_path"]
    assert file_hash(local) == record["sha256"]
    tree = ast.parse(local.read_text(encoding="utf-8"))
    function = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name
    )
    # Extract only the reviewed pure function. No upstream imports, clients, or generated
    # candidate programs are executed. This is a test harness, not a Python sandbox.
    module = ast.Module(body=[function], type_ignores=[])
    scope = {} if namespace is None else dict(namespace)
    exec(compile(module, str(local), "exec", flags=__future__.annotations.compiler_flag), scope)  # noqa: S102 - reviewed, pinned upstream test functions only
    return scope[name]


def test_all_upstream_sources_and_licenses_are_pinned():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8-sig"))
    assert len(manifest["files"]) == 13
    for row in manifest["files"]:
        assert row["commit"] == PINS[row["repo"]]
        assert file_hash(ROOT / row["local_path"]) == row["sha256"]
    assert sum(row["upstream_path"] == "LICENSE" for row in manifest["files"]) == 2


def test_eoh_parent_draws_match_upstream_across_seeds():
    population = [{"objective": i, "id": i} for i in range(7)]
    for seed in range(25):
        reference = upstream(
            "eoh/src/eoh/methods/selection/prob_rank.py",
            "parent_selection",
            {"random": random.Random(seed)},
        )
        assert eoh_parents(population, 20, random.Random(seed)) == reference(population, 20)


def test_eoh_survival_matches_upstream_ties_failures_and_population_sizes():
    reference = upstream(
        "eoh/src/eoh/methods/management/pop_greedy.py", "population_management", {"heapq": heapq}
    )
    population = [
        {"id": i, "objective": score} for i, score in enumerate([None, 8, 2, 2, 4, -1, None, 8])
    ]
    for size in (0, 1, 3, 8, 20):
        assert eoh_survivors(population, size) == reference(population, size)
    assert eoh_survivors(population, 20)[1]["id"] == 2


def test_funsearch_signature_and_reduction_match_upstream():
    path = "implementation/programs_database.py"
    signature = upstream(path, "_get_signature")
    reduction = upstream(path, "_reduce_score")
    # Insertion order differs from lexical key order; scores must not be averaged.
    for scores in ({"z": -3, "a": -10}, {"a": -10, "z": -3}, {"x": 2}):
        assert funsearch_signature(scores) == signature(scores)
        assert funsearch_reduced_score(scores) == reduction(scores)


def test_funsearch_benchmark_adapter_optimizes_aggregate_not_last_stream():
    scores = funsearch_scores(
        {
            "instances": [
                {"instance_id": "train/z", "bins": 2},
                {"instance_id": "train/a", "bins": 5},
            ],
            "total_bins": 7,
        }
    )
    assert funsearch_reduced_score(scores) == -7
    assert funsearch_signature(scores) == (-7, -5, -2)


def test_funsearch_schedule_and_length_preferences():
    assert funsearch_temperature(0) == funsearch_temperature(30000) == 0.1
    assert funsearch_temperature(15000) == 0.05
    assert 0 < funsearch_temperature(29999) < 0.000004
    assert funsearch_length_probabilities([10, 10]) == [0.5, 0.5]
    probabilities = funsearch_length_probabilities([10, 20, 40])
    assert probabilities[0] > probabilities[1] > probabilities[2]
    assert sum(probabilities) == pytest.approx(1)
