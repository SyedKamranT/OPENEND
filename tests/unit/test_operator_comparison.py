import random

from openend.benchmark_diagnostics import policies
from openend.operator_comparison import conservative_mutate
from openend.utility_runner import parse


def flatten(tree):
    if not isinstance(tree, list):
        return [tree]
    return [tree[0]] + [token for child in tree[1:] for token in flatten(child)]


def test_single_token_proposals_preserve_tree_and_change_exactly_one_token():
    for parent in policies().values():
        original = flatten(parent.to_object()["expression"])
        for seed in range(30):
            response = conservative_mutate(parent, random.Random(seed))
            assert response == conservative_mutate(parent, random.Random(seed))
            child = parse(response)
            tokens = flatten(child.to_object()["expression"])
            assert len(original) == len(tokens)
            assert sum(a != b for a, b in zip(original, tokens)) == 1
