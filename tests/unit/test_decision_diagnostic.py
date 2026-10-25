import itertools

import pytest

from openend.benchmark import Instance, check_certificate, reference_pack
from openend.decision_diagnostic import actions, place, trace


def test_host_forbids_optional_opening():
    assert actions(4, [6, 3]) == [0]
    with pytest.raises(ValueError, match="illegal"):
        place(4, [6, 3], 2, 10)


def test_all_small_streams_preserve_prefix_and_never_worsen_rollout():
    for items in itertools.product((2, 4, 6, 8), repeat=4):
        instance = Instance("tiny", "test", 10, items)
        baseline = trace(instance)
        rollout = trace(instance, hindsight=True)
        assert (baseline["bins"], baseline["assignments"]) == reference_pack("best_fit", instance)
        assert rollout["bins"] <= baseline["bins"]
        for row in (baseline, rollout):
            previous = None
            for state in row["states"]:
                step = state["step"]
                cert = state["best_certificate"]
                assert cert[:step] == row["assignments"][:step]
                assert check_certificate(instance, cert) == state["best_completion_bins"]
                assert cert[step] in actions(items[step], state["remaining"])
                if row is rollout and previous is not None:
                    assert state["best_completion_bins"] <= previous
                previous = state["best_completion_bins"]
