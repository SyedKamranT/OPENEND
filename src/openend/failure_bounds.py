"""Finite-study missing-outcome bounds; these are not confidence intervals."""

import math
import statistics


def packing_bounds(instances):
    """Bounds for any feasible complete packing of this already specified suite."""
    if not instances:
        raise ValueError("empty suite")
    return sum(x.lower_bound for x in instances), sum(len(x.items) for x in instances)


def mean_difference_bounds(records, expected_pairs):
    """Retain every planned block/run; bound unknown arm outcomes instead of dropping them.

    Each record has block/run plus uniform and weighted arm dictionaries with lower,
    upper and observed (null for unknown) bin counts. All planned pairs must be present.
    Equal runs per block and equal block weights define the finite-study estimand.
    """
    expected = list(expected_pairs)
    keys = [(r["block"], r["run"]) for r in records]
    if (
        not expected
        or len(set(expected)) != len(expected)
        or len(set(keys)) != len(keys)
        or set(keys) != set(expected)
    ):
        raise ValueError("exact planned pair roster required")
    blocks, unknown = {}, 0
    for row in records:
        intervals = []
        for arm in ("uniform", "weighted"):
            value = row[arm]
            lower, upper, observed = value["lower"], value["upper"], value["observed"]
            if any(type(x) is not int or x < 1 for x in (lower, upper)) or lower > upper:
                raise ValueError("invalid packing bounds")
            if observed is None:
                unknown += 1
                intervals.append((lower, upper))
            elif (
                type(observed) is not int
                or not math.isfinite(observed)
                or not lower <= observed <= upper
            ):
                raise ValueError("observation outside bounds")
            else:
                intervals.append((observed, observed))
        u, w = intervals
        blocks.setdefault(row["block"], []).append((u[0] - w[1], u[1] - w[0]))
    if len({len(rows) for rows in blocks.values()}) != 1:
        raise ValueError("unbalanced planned runs")
    bound = [
        statistics.mean(statistics.mean(pair[i] for pair in rows) for rows in blocks.values())
        for i in (0, 1)
    ]
    return {
        "finite_study_mean_bounds": bound,
        "unknown_arm_outcomes": unknown,
        "planned_pairs": len(expected),
        "blocks": len(blocks),
        "scope": "identification_bounds_not_sampling_uncertainty",
        "limitations": "Requires feasible completed-output bounds; unknown usage remains unknown. "
        "Does not repair interrupted budgets or certify a complete randomized comparison.",
    }
