import random

import pytest

from openend.policy import Policy
from openend.utility_state import UtilityState


def test_bin_count_controls_archive_prompt_and_selection_despite_fitness_reversal():
    first = Policy.from_object({"expression": 0})
    equivalent = Policy.from_object({"expression": ["mul", "gap", "exact_fit"]})
    state = UtilityState([("reference", first, {"total_bins": 100, "fitness": 0.99})])
    state.observe(equivalent, {"total_bins": 99, "fitness": 0.01})
    request = state.request(random.Random(1), weighted=True)
    assert request["parent"] == equivalent.to_object()
    assert request["training_total_bins"] == 99
    assert state.selected()["policy"] == equivalent.to_object()
    assert not state.selected()["used_fallback"]
    # Same-cell worse total must not replace even when its ratio fitness is higher.
    state.observe(first, {"total_bins": 101, "fitness": 1})
    assert state.request(random.Random(1), False)["training_total_bins"] == 99


def test_reference_fallback_and_stable_generated_ties():
    first = Policy.from_object({"expression": 0})
    second = Policy.from_object({"expression": 1})
    state = UtilityState(
        [("first", first, {"total_bins": 100}), ("second", second, {"total_bins": 100})]
    )
    state.observe(second, {"total_bins": 100})
    assert state.selected()["origin"] == "first" and state.selected()["used_fallback"]
    state.observe(first, {"total_bins": 99})
    state.observe(second, {"total_bins": 99})
    assert state.selected()["origin"] == 1
    detached = state.selected()
    detached["policy"]["expression"] = 10
    assert state.selected_policy() == first
    with pytest.raises(ValueError):
        state.observe(first, {"total_bins": -1})
