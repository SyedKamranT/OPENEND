"""Audited baseline primitives, NOT complete EoH or FunSearch implementations.

Source pins and licenses: data/baselines/upstream-v1/manifest.json.
EoH: MIT, Fei Liu. FunSearch: Apache-2.0, DeepMind Technologies Limited.
Adapters below isolate testable mechanics; native program search remains unfinished.
"""

import math


def eoh_parents(population, count, rng):
    # Upstream uses ordered population rank, not objective-proportional roulette.
    return rng.choices(
        population, weights=[1 / (i + 1 + len(population)) for i in range(len(population))], k=count
    )


def eoh_survivors(population, size):
    seen, eligible = set(), []
    for candidate in population:
        score = candidate["objective"]
        if score is not None and score not in seen:
            eligible.append(candidate)
            seen.add(score)
    return sorted(eligible, key=lambda p: p["objective"])[:size]


def funsearch_signature(scores):
    return tuple(scores[key] for key in sorted(scores))


def funsearch_reduced_score(scores):
    # Faithful upstream reduction: last INSERTED test score, not mean or max.
    return scores[next(reversed(scores))]


def funsearch_scores(evaluation):
    """Explicit benchmark adaptation: append aggregate objective last.

    Higher is better. Per-stream entries still define behavioral score clusters.
    Naming the aggregate ensures callers cannot accidentally optimize the last stream.
    """
    scores = {row["instance_id"]: -row["bins"] for row in evaluation["instances"]}
    if "aggregate" in scores:
        raise ValueError("reserved aggregate key")
    scores["aggregate"] = -evaluation["total_bins"]
    return scores


def funsearch_temperature(registrations, initial=0.1, period=30000):
    if registrations < 0 or initial <= 0 or period <= 0:
        raise ValueError("invalid temperature schedule")
    return initial * (1 - (registrations % period) / period)


def softmax(values, temperature):
    if not values or temperature <= 0 or any(not math.isfinite(x) for x in values):
        raise ValueError("finite nonempty scores and positive temperature required")
    top = max(values)
    weights = [math.exp((x - top) / temperature) for x in values]
    total = sum(weights)
    return [weight / total for weight in weights]


def funsearch_length_probabilities(lengths):
    if not lengths or min(lengths) < 0:
        raise ValueError("invalid program lengths")
    normalized = [-(x - min(lengths)) / (max(lengths) + 1e-6) for x in lengths]
    return softmax(normalized, 1.0)
