"""Domain-separated, public development blocks; never confirmatory holdouts."""

import random
from dataclasses import asdict

from .artifacts import digest
from .benchmark import FAMILIES, Instance

VERSION = "development-blocks-v1"


def suite(master_seed, block, role, per_family=12):
    if type(master_seed) is not int or not 0 <= master_seed < 2**64:
        raise ValueError("invalid master seed")
    if type(block) is not int or not 0 <= block < 10000:
        raise ValueError("invalid block")
    if role not in ("train", "development_eval"):
        raise ValueError("only development roles supported")
    if type(per_family) is not int or not 1 <= per_family <= 100:
        raise ValueError("invalid suite size")
    result = []
    for family in FAMILIES:
        for index in range(per_family):
            seed = int(digest([VERSION, master_seed, block, role, family, index]), 16)
            rng = random.Random(seed)
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
                    items.extend([size, 100 - size])
                optimum = 30
            else:
                items = []
                for _ in range(20):
                    a, b = rng.randint(20, 40), rng.randint(20, 40)
                    items.extend([a, b, 100 - a - b])
                optimum = 20
            rng.shuffle(items)
            result.append(
                Instance(
                    f"{role}/development-block-{block}/{family}/{index:03}",
                    family,
                    100,
                    tuple(items),
                    optimum,
                )
            )
    return tuple(result)


def record(master_seed, block, role, per_family=12):
    instances = [asdict(x) for x in suite(master_seed, block, role, per_family)]
    return {
        "version": VERSION,
        "scope": "public_development_not_confirmation",
        "master_seed": master_seed,
        "block": block,
        "role": role,
        "per_family": per_family,
        "instances": instances,
        "sha256": digest(instances),
    }
