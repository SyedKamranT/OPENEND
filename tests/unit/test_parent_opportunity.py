from openend.parent_opportunity import retained_gain


def test_invalid_and_worse_proposals_cannot_improve_incumbent():
    assert retained_gain(None, 1476) == 0
    assert retained_gain({"total_bins": 1600}, 1476) == 0
    assert retained_gain({"total_bins": 1476}, 1476) == 0
    assert retained_gain({"total_bins": 1475}, 1476) == 1
