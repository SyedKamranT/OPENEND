import math
import statistics

import pytest

from openend.utility_planning import simulate, summarize


def rows(values):
    return [
        {"block": i, "run": 0, "difference": value, "complete": True}
        for i, value in enumerate(values)
    ]


def test_equal_block_weight_and_pseudoreplication():
    base = summarize(rows([0, 2, 4, 6]))
    replicated = [{**row, "run": r} for row in rows([0, 2, 4, 6]) for r in range(5)]
    larger = summarize(replicated)
    assert base["mean_difference"] == 3
    assert base["standard_error"] == pytest.approx(math.sqrt(20 / 3) / 2)
    assert larger["standard_error"] == base["standard_error"]
    assert larger["blocks"] == 4 and larger["paired_runs"] == 20


def test_unknown_failure_duplicate_and_zero_variance():
    for invalid in (
        [*rows([1, 2]), rows([1])[0]],
        [{**row, "complete": False} for row in rows([1, 2])],
        rows([1, float("nan")]),
    ):
        with pytest.raises(ValueError):
            summarize(invalid)
    assert summarize(rows([0] * 20))["normal_approximation_interval"] is None
    assert summarize(rows([2]))["standard_error"] is None


def test_simulation_deterministic_and_failures_not_dropped():
    options = {
        "blocks": 8,
        "runs": 2,
        "effect": 2,
        "block_sd": 2,
        "run_sd": 2,
        "zero_probability": 0,
        "failure_probability": 0,
        "repetitions": 20,
        "seed": 3,
    }
    assert simulate(**options) == simulate(**options)
    failed = simulate(**{**options, "failure_probability": 1})
    assert failed["incomplete_repetitions"] == 20
    assert failed["positive_lower_bound_fraction_all_repetitions"] == 0
    assert failed["conditional_interval_coverage"] is None
    ties = simulate(**{**options, "zero_probability": 1})
    assert ties["degenerate_repetitions"] == 20
    assert ties["assumptions"]["expected_difference"] == 0


def test_student_uses_independent_block_degrees_of_freedom():
    base = rows(range(8))
    result = summarize(base, "student")
    assert result["student_critical"] == 2.365
    assert result["student_interval"][0] == pytest.approx(
        3.5 - 2.365 * statistics.stdev(range(8)) / math.sqrt(8)
    )
    repeated = [{**row, "run": r} for row in base for r in range(4)]
    assert summarize(repeated, "student")["student_interval"] == result["student_interval"]
    with pytest.raises(ValueError, match="blocks only"):
        summarize(rows(range(9)), "student")
    assert summarize(rows([0] * 8), "student")["student_interval"] is None
