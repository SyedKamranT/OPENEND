import pytest

from openend.equivalence import certify
from openend.policy import Policy


@pytest.mark.parametrize(
    "expression,match",
    [
        (["sub", 1, "gap"], "best_fit"),
        (["add", "remaining", "item"], "worst_fit"),
        ("item", "first_fit"),
        (["div", "gap", 0], "first_fit"),
        # Floating-point absorption must not be falsely called strictly monotone.
        (["add", 1, ["mul", 1e-300, "gap"]], "first_fit"),
        # Actual interpreter clipping makes this score constant.
        (["div", 10, 0.000001], "first_fit"),
    ],
)
def test_complete_domain_certificates_respect_actual_arithmetic(expression, match):
    policy = Policy.from_object({"expression": expression})
    result = certify(policy)
    assert result["verdict"] == "known_reference_equivalent"
    assert result["matches"] == [match]
    assert result["states_checked"] == 5050
    # Compare against independent imperative choice definitions in adversarial bin orders.
    for item in range(1, 100):
        for spaces in ([item + 1, item], [item, 100, item + 1], [0, item + 1, item]):
            feasible = [i for i, remaining in enumerate(spaces) if remaining >= item]
            expected = (
                feasible[0]
                if match == "first_fit"
                else min(feasible, key=lambda i: (spaces[i], i))
                if match == "best_fit"
                else max(feasible, key=lambda i: (spaces[i], -i))
            )
            assert policy.choose(item, spaces, 100) == expected


def test_probe_collision_does_not_become_false_equivalence_certificate():
    bonus = Policy.from_object({"expression": ["add", "gap", ["mul", 2, "exact_fit"]]})
    result = certify(bonus)
    assert result["verdict"] == "unresolved" and result["matches"] == []
    assert result["global_novelty"] == "unresolved"


def test_unsupported_index_dependence_abstains():
    result = certify(Policy.from_object({"expression": ["neg", "index"]}))
    assert result["verdict"] == "unresolved"
    assert "not implemented" in result["reason"]
