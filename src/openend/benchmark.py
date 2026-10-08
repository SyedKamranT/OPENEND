"""Integer online bin packing with independent certificate checking and references."""

import math
import random
from collections import Counter
from dataclasses import asdict, dataclass

from .artifacts import digest

CAPACITY = 100
FAMILIES = ("uniform", "bimodal", "paired", "triplets")
SPLIT_SEEDS = {"train": 1729, "validation": 2718, "test": 31415}
SUITE_VERSION = "binpack-pilot-v1"


@dataclass(frozen=True)
class Instance:
    instance_id: str
    family: str
    capacity: int
    items: tuple[int, ...]
    known_optimum: int | None = None

    def __post_init__(self):
        if type(self.capacity) is not int or not 1 <= self.capacity <= 10000:
            raise ValueError("invalid capacity")
        if not self.items or len(self.items) > 1000:
            raise ValueError("invalid item count")
        if any(type(x) is not int or not 1 <= x <= self.capacity for x in self.items):
            raise ValueError("items must be positive integers no larger than capacity")

    @property
    def lower_bound(self):
        return max(
            math.ceil(sum(self.items) / self.capacity),
            sum(x > self.capacity / 2 for x in self.items),
        )


def make_suite(split, per_family=12):
    if split not in SPLIT_SEEDS or type(per_family) is not int or not 1 <= per_family <= 100:
        raise ValueError("invalid split or suite size")
    suite = []
    for family_index, family in enumerate(FAMILIES):
        rng = random.Random(SPLIT_SEEDS[split] + 100000 * family_index)
        for index in range(per_family):
            optimum = None
            if family == "uniform":
                items = [rng.randint(1, 99) for _ in range(60)]
            elif family == "bimodal":
                items = [
                    rng.randint(20, 35) if rng.random() < 0.5 else rng.randint(65, 80)
                    for _ in range(60)
                ]
            elif family == "paired":
                items = []
                for _ in range(30):
                    size = rng.randint(15, 49)
                    items.extend([size, CAPACITY - size])
                optimum = 30
            else:
                items = []
                for _ in range(20):
                    a, b = rng.randint(20, 40), rng.randint(20, 40)
                    items.extend([a, b, CAPACITY - a - b])
                optimum = 20
            rng.shuffle(items)
            suite.append(
                Instance(f"{split}/{family}/{index:03}", family, CAPACITY, tuple(items), optimum)
            )
    return tuple(suite)


def suite_record(split, per_family):
    instances = [asdict(x) for x in make_suite(split, per_family)]
    return {
        "version": SUITE_VERSION,
        "split": split,
        "instances": instances,
        "sha256": digest(instances),
    }


def check_certificate(instance, assignments):
    """Validate a complete packing independently of the policy interpreter."""
    if len(assignments) != len(instance.items):
        raise ValueError("missing or extra item assignments")
    loads = []
    for item, bin_index in zip(instance.items, assignments):
        if type(bin_index) is not int or not 0 <= bin_index <= len(loads):
            raise ValueError("invalid or non-contiguous bin index")
        if bin_index == len(loads):
            loads.append(0)
        loads[bin_index] += item
        if loads[bin_index] > instance.capacity:
            raise ValueError("capacity exceeded")
    return len(loads)


def pack(policy, instance):
    remaining, assignments = [], []
    for item in instance.items:
        index = policy.choose(item, remaining, instance.capacity)
        if index == len(remaining):
            remaining.append(instance.capacity)
        remaining[index] -= item
        assignments.append(index)
    bins = check_certificate(instance, assignments)
    return bins, assignments


def reference_pack(name, instance):
    """Separate imperative implementation, not the expression evaluator."""
    loads, assignments = [], []
    for item in instance.items:
        feasible = [i for i, load in enumerate(loads) if load + item <= instance.capacity]
        if not feasible:
            selected = len(loads)
            loads.append(0)
        elif name == "first_fit":
            selected = feasible[0]
        elif name == "best_fit":
            selected = max(feasible, key=lambda i: (loads[i], -i))
        elif name == "worst_fit":
            selected = min(feasible, key=lambda i: (loads[i], i))
        else:
            raise ValueError("unknown reference")
        loads[selected] += item
        assignments.append(selected)
    return check_certificate(instance, assignments), assignments


def evaluate(policy, suite):
    rows = []
    for instance in suite:
        bins, assignments = pack(policy, instance)
        rows.append(
            {
                "instance_id": instance.instance_id,
                "family": instance.family,
                "bins": bins,
                "lower_bound": instance.lower_bound,
                "known_optimum": instance.known_optimum,
                "assignment_sha256": digest(assignments),
            }
        )
    if not rows:
        raise ValueError("suite must be nonempty")
    families = sorted({r["family"] for r in rows})
    fitness = sum(r["lower_bound"] / r["bins"] for r in rows) / len(rows)
    return {
        "valid": True,
        "fitness": fitness,
        "total_bins": sum(r["bins"] for r in rows),
        "family_bins": {f: sum(r["bins"] for r in rows if r["family"] == f) for f in families},
        "instances": rows,
    }


def reference_scores(suite):
    totals = {}
    for name in ("first_fit", "best_fit", "worst_fit"):
        counts = Counter()
        for instance in suite:
            counts[instance.family] += reference_pack(name, instance)[0]
        totals[name] = {"total_bins": sum(counts.values()), "family_bins": dict(counts)}
    return totals


def successful(result, references, minimum_improvement=0.01):
    """Predeclared pilot utility screen, not a statistical superiority claim."""
    reference = min(references.values(), key=lambda r: r["total_bins"])
    return result["total_bins"] <= (1 - minimum_improvement) * reference["total_bins"] and all(
        result["family_bins"][f] <= 1.05 * total for f, total in reference["family_bins"].items()
    )
