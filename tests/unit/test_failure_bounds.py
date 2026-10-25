import pytest

from openend.benchmark import Instance
from openend.failure_bounds import mean_difference_bounds, packing_bounds


def test_missing_outcomes_retained_and_bounds_narrow_on_completion():
    rows = [
        {
            "block": 0,
            "run": 0,
            "uniform": {"lower": 2, "upper": 10, "observed": 5},
            "weighted": {"lower": 2, "upper": 10, "observed": 4},
        },
        {
            "block": 1,
            "run": 0,
            "uniform": {"lower": 2, "upper": 10, "observed": 6},
            "weighted": {"lower": 2, "upper": 10, "observed": None},
        },
    ]
    roster = [(0, 0), (1, 0)]
    result = mean_difference_bounds(rows, roster)
    assert result["finite_study_mean_bounds"] == [-1.5, 2.5]
    assert result["unknown_arm_outcomes"] == 1
    for completion in range(2, 11):
        rows[1]["weighted"]["observed"] = completion
        complete = mean_difference_bounds(rows, roster)["finite_study_mean_bounds"]
        assert complete[0] == complete[1]
        assert -1.5 <= complete[0] <= 2.5
    with pytest.raises(ValueError, match="roster"):
        mean_difference_bounds(rows[:1], roster)


def test_data_only_bounds_and_invalid_observed_counts():
    data = [Instance("train/a", "paired", 100, (60, 40, 60, 40))]
    assert packing_bounds(data) == (2, 4)
    with pytest.raises(ValueError, match="outside"):
        mean_difference_bounds(
            [
                {
                    "block": 0,
                    "run": 0,
                    "uniform": {"lower": 2, "upper": 4, "observed": 5},
                    "weighted": {"lower": 2, "upper": 4, "observed": None},
                }
            ],
            [(0, 0)],
        )
