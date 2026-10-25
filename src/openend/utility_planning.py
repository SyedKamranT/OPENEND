"""Synthetic design sensitivity; never a confirmatory analysis or empirical power claim."""

import argparse
import math
import random
import statistics
from pathlib import Path

from .artifacts import file_hash, snapshot_source, source_manifest, write_json

# NIST t table, 0.975 column, rounded to three decimals as published.
# https://www.itl.nist.gov/div898/handbook/eda/section3/eda3672.htm
STUDENT_975 = {7: 2.365, 15: 2.131, 31: 2.040, 63: 1.998}


def summarize(rows, interval_method="normal"):
    """Average paired run differences within independent blocks, then weight blocks equally."""
    if not rows:
        raise ValueError("empty design")
    blocks, seen = {}, set()
    for row in rows:
        key = (row["block"], row["run"])
        if key in seen:
            raise ValueError("duplicate paired run")
        seen.add(key)
        value = row["difference"]
        if row.get("complete") is not True or value is None:
            raise ValueError("incomplete pair: no silent complete-case analysis")
        if type(value) not in (float, int) or not math.isfinite(value):
            raise ValueError("nonfinite difference")
        blocks.setdefault(row["block"], []).append(value)
    if len({len(values) for values in blocks.values()}) != 1:
        raise ValueError("unbalanced runs per block")
    means = [statistics.mean(values) for values in blocks.values()]
    if interval_method not in ("normal", "student"):
        raise ValueError("unknown interval method")
    if interval_method == "student" and len(means) - 1 not in STUDENT_975:
        raise ValueError("Student planning supports 8, 16, 32 or 64 blocks only")
    mean = statistics.mean(means)
    se = statistics.stdev(means) / math.sqrt(len(means)) if len(means) > 1 else None
    interval = [mean - 1.96 * se, mean + 1.96 * se] if se and se > 0 else None
    result = {
        "blocks": len(means),
        "runs_per_block": len(rows) // len(means),
        "paired_runs": len(rows),
        "mean_difference": mean,
        "block_means": means,
        "standard_error": se,
        "normal_approximation_interval": interval,
        "status": "planning_only" if interval else "insufficient_variation_or_blocks",
    }
    if interval_method == "student":
        critical = STUDENT_975[len(means) - 1]
        result["student_interval"] = [mean - critical * se, mean + critical * se] if se else None
        result["student_critical"] = critical
    return result


def simulate(
    *,
    blocks,
    runs,
    effect,
    block_sd,
    run_sd,
    zero_probability,
    failure_probability,
    repetitions,
    seed,
    practical_margin=1.0,
    interval_method="normal",
):
    for name, value in (("blocks", blocks), ("runs", runs), ("repetitions", repetitions)):
        if type(value) is not int or value < (2 if name == "blocks" else 1):
            raise ValueError(f"invalid {name}")
    for value in (effect, block_sd, run_sd, practical_margin):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("invalid finite parameter")
    if min(block_sd, run_sd, practical_margin) < 0:
        raise ValueError("negative scale or margin")
    if not all(0 <= p <= 1 for p in (zero_probability, failure_probability)):
        raise ValueError("invalid probability")
    if interval_method not in ("normal", "student"):
        raise ValueError("unknown interval method")
    if interval_method == "student" and blocks - 1 not in STUDENT_975:
        raise ValueError("unsupported Student block count")
    rng = random.Random(seed)
    accepted = above_zero = above_margin = covered = degenerate = incomplete = 0
    target = (1 - zero_probability) * effect
    widths = []
    for _ in range(repetitions):
        rows = []
        for block in range(blocks):
            shared = rng.gauss(0, block_sd)
            for run in range(runs):
                difference = effect + shared + rng.gauss(0, run_sd)
                if rng.random() < zero_probability:
                    difference = 0.0
                complete = rng.random() >= failure_probability
                rows.append(
                    {
                        "block": block,
                        "run": run,
                        "difference": difference if complete else None,
                        "complete": complete,
                    }
                )
        if any(not row["complete"] for row in rows):
            incomplete += 1
            continue
        result = summarize(rows, interval_method)
        interval = result[
            "student_interval" if interval_method == "student" else "normal_approximation_interval"
        ]
        if interval is None:
            degenerate += 1
            continue
        accepted += 1
        low, high = interval
        above_zero += low > 0
        above_margin += low > practical_margin
        covered += low <= target <= high
        widths.append(high - low)
    return {
        "assumptions": {
            "interval_method": interval_method,
            "blocks": blocks,
            "runs_per_block": runs,
            "effect_before_zero_mixture": effect,
            "expected_difference": target,
            "block_sd": block_sd,
            "run_sd": run_sd,
            "zero_probability": zero_probability,
            "failure_probability": failure_probability,
            "repetitions": repetitions,
            "seed": seed,
            "practical_margin": practical_margin,
        },
        "complete_nondegenerate_repetitions": accepted,
        "incomplete_repetitions": incomplete,
        "degenerate_repetitions": degenerate,
        "positive_lower_bound_fraction_all_repetitions": above_zero / repetitions,
        "practical_lower_bound_fraction_all_repetitions": above_margin / repetitions,
        "conditional_interval_coverage": covered / accepted if accepted else None,
        "coverage_monte_carlo_se": math.sqrt(
            (covered / accepted) * (1 - covered / accepted) / accepted
        )
        if accepted
        else None,
        "mean_interval_width": statistics.mean(widths) if widths else None,
    }


def run(output, root, interval_method="normal"):
    output, root = Path(output), Path(root)
    output.mkdir(parents=True, exist_ok=False)
    scenarios = [
        ("null", 0.0, 0.0, 0.0),
        ("one_bin", 1.0, 0.0, 0.0),
        ("two_bins", 2.0, 0.0, 0.0),
        ("mostly_ties", 2.0, 0.75, 0.0),
        ("failures", 2.0, 0.0, 0.01),
    ]
    results = []
    for blocks in (8, 16, 32, 64):
        for runs in (1, 4):
            for name, effect, zeros, failures in scenarios:
                result = simulate(
                    blocks=blocks,
                    runs=runs,
                    effect=effect,
                    block_sd=2.0,
                    run_sd=2.0,
                    zero_probability=zeros,
                    failure_probability=failures,
                    repetitions=1000,
                    seed=20261014,
                    practical_margin=1.0,
                    interval_method=interval_method,
                )
                results.append({"scenario": name, **result})
    source = source_manifest(root)
    snapshot_source(root, source, output / "source.zip")
    write_json(
        output / "sensitivity.json",
        {
            "status": "synthetic_planning_not_empirical_power",
            "interval_method": interval_method,
            "results": results,
            "limitations": "Gaussian block/run differences with optional zero mixture and independent "
            "pair failure. Scales are illustrative bins per fixed suite, not pilot-fitted. Intervals "
            "are diagnostic and may undercover, especially outside Gaussian block means. "
            "Student values are rounded NIST table entries. No sample size selected; no model or holdout calls.",
        },
    )
    write_json(
        output / "run_manifest.json",
        {
            "experiment_kind": "utility-planning-v1"
            if interval_method == "normal"
            else "utility-planning-student-v2",
            "status": "completed",
            "source": source,
            "input_files": {},
            "output_files": {p.name: file_hash(p) for p in output.iterdir()},
        },
    )
    return {"scenarios": len(results), "simulated_studies": 1000 * len(results), "model_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--interval", choices=("normal", "student"), default="normal")
    args = parser.parse_args()
    print(run(args.output, Path.cwd(), args.interval))


if __name__ == "__main__":
    main()
