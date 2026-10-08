import itertools
import json
import random

import pytest

from openend.benchmark import (
    Instance,
    check_certificate,
    make_suite,
    pack,
    reference_pack,
    suite_record,
)
from openend.policy import REFERENCES, InvalidPolicy, Policy
from openend.search import Archive, novelty_screen, signature, sparsity


def optimum(items, capacity):
    """Tiny exhaustive oracle, independent of the candidate engine."""
    best = len(items)

    def visit(index, loads):
        nonlocal best
        if index == len(items):
            best = min(best, len(loads))
            return
        if len(loads) >= best:
            return
        item = items[index]
        for bin_index in range(len(loads)):
            if loads[bin_index] + item <= capacity:
                new_loads = loads.copy()
                new_loads[bin_index] += item
                visit(index + 1, new_loads)
        visit(index + 1, loads + [item])

    visit(0, [])
    return best


def test_reference_policies_match_independent_implementations_exhaustively():
    for items in itertools.product([2, 4, 6, 8], repeat=4):
        instance = Instance("tiny", "test", 10, items)
        lower = optimum(items, 10)
        for name, policy in REFERENCES.items():
            count, assignment = pack(policy, instance)
            assert (count, assignment) == reference_pack(name, instance)
            assert lower <= count <= len(items)
            assert instance.lower_bound <= lower


def test_stable_ties_and_online_prefix():
    prefix = Instance("a", "test", 10, (6, 6, 4))
    extended = Instance("b", "test", 10, (6, 6, 4, 4, 2))
    for policy in REFERENCES.values():
        assert pack(policy, prefix)[1] == pack(policy, extended)[1][:3]
    assert pack(REFERENCES["first_fit"], prefix)[1] == [0, 1, 0]


@pytest.mark.parametrize("assignment", [[0], [0, 0, 0], [0, 2], [-1, 0], [True, 0]])
def test_invalid_certificates_are_rejected(assignment):
    with pytest.raises(ValueError):
        check_certificate(Instance("bad", "test", 10, (6, 6)), assignment)


@pytest.mark.parametrize(
    "value",
    [
        {"expression": "__import__('os')"},
        {"expression": ["exec", "item"]},
        {"expression": float("nan")},
        {"expression": float("inf")},
        {"expression": True},
        {"expression": 11},
        {"expression": ["add", 1]},
        {"expression": 1, "code": "x"},
        {"expression": {}},
        {"expression": ["add", 1, 2, 3]},
    ],
)
def test_untrusted_policies_fail_closed(value):
    with pytest.raises(InvalidPolicy):
        Policy.from_object(value)


def test_depth_bytes_and_duplicate_keys():
    tree = 1
    for _ in range(8):
        tree = ["neg", tree]
    for text in [
        json.dumps({"expression": tree}),
        " " * 17000,
        '{"expression":0,"expression":1}',
        '```json\n{"expression":0}\n```',
    ]:
        with pytest.raises(InvalidPolicy):
            Policy.from_text(text)


def test_protected_division_has_defined_ties():
    policy = Policy.from_object({"expression": ["div", "gap", 0]})
    assert policy.choose(5, [9, 8], 10) == 0


def test_reproducible_disjoint_splits_and_planted_bounds():
    seen = set()
    for split in ("train", "validation", "test"):
        record = suite_record(split, 3)
        assert record == suite_record(split, 3)
        for instance in make_suite(split, 3):
            assert instance.items not in seen
            seen.add(instance.items)
            if instance.known_optimum:
                assert sum(instance.items) == instance.capacity * instance.known_optimum
                assert instance.lower_bound == instance.known_optimum


def test_novelty_does_not_promote_finite_probe_differences_to_discoveries():
    assert novelty_screen(REFERENCES["best_fit"])["verdict"] == "known_reference"
    reworded = Policy.from_object({"expression": ["sub", 0, "gap"]})
    assert novelty_screen(reworded)["verdict"] == "unresolved"
    assert "best_fit" in novelty_screen(reworded)["probe_matches"]


def test_sparse_parent_selection_increases_sampling_of_sparse_elites():
    archive = Archive(10)
    for policy in REFERENCES.values():
        archive.insert(policy, 0.9)
    archive.insert(Policy.from_object({"expression": "index"}), 0.95)
    off_rng, on_rng = random.Random(91), random.Random(91)
    off = [sparsity(signature(archive.select(off_rng, False)[0])) for _ in range(3000)]
    on = [sparsity(signature(archive.select(on_rng, True)[0])) for _ in range(3000)]
    assert sum(on) > sum(off)


def test_archive_retains_better_elite_and_capacity():
    archive = Archive(6)
    first = REFERENCES["best_fit"]
    archive.insert(first, 0.8)
    archive.insert(first, 0.2)
    assert archive.summary()["qd_score"] == 0.8
    assert archive.summary()["total_cells"] == 36
