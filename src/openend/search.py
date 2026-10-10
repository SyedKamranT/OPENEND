"""Identical QD machinery; only parent-selection weights differ between arms."""

import random

from .artifacts import digest
from .policy import REFERENCES


def probes():
    rng = random.Random(8675309)
    return tuple(
        (rng.randint(5, 45), tuple(rng.randint(46, 100) for _ in range(6))) for _ in range(32)
    )


PROBES = probes()


def signature(policy):
    return tuple(policy.choose(item, spaces, 100) for item, spaces in PROBES)


def distance(a, b):
    if len(a) != len(b) or not a:
        raise ValueError("incompatible signatures")
    return sum(x != y for x, y in zip(a, b)) / len(a)


REFERENCE_SIGNATURES = tuple(signature(p) for p in REFERENCES.values())


def sparsity(sig):
    # Fixed reference population; larger distance means sparser, never invert this value.
    return sum(sorted(distance(sig, other) for other in REFERENCE_SIGNATURES)[:2]) / 2


def descriptor(sig):
    gap = sum((spaces[index] - item) / 100 for (item, spaces), index in zip(PROBES, sig))
    position = sum(index / 5 for index in sig)
    return gap / len(sig), position / len(sig)


class Archive:
    def __init__(self, resolution=6):
        self.resolution = resolution
        self.cells = {}

    def insert(self, policy, fitness):
        sig = signature(policy)
        cell = tuple(min(self.resolution - 1, int(x * self.resolution)) for x in descriptor(sig))
        incumbent = self.cells.get(cell)
        if incumbent is None or fitness > incumbent[1]:
            self.cells[cell] = (policy, fitness, sig)

    def select(self, rng, sparse):
        elites = [self.cells[key] for key in sorted(self.cells)]
        if not elites:
            raise ValueError("archive is empty")
        weights = [0.05 + sparsity(x[2]) if sparse else 1.0 for x in elites]
        return rng.choices(elites, weights=weights, k=1)[0]

    def summary(self):
        return {
            "occupied_cells": len(self.cells),
            "total_cells": self.resolution**2,
            "coverage": len(self.cells) / self.resolution**2,
            "qd_score": sum(x[1] for x in self.cells.values()),
        }

    def selection_diagnostics(self, sparse):
        elites = [self.cells[key] for key in sorted(self.cells)]
        weights = [0.05 + sparsity(x[2]) if sparse else 1.0 for x in elites]
        probabilities = [weight / sum(weights) for weight in weights]
        return {
            "policy_ids": [entry[0].identity for entry in elites],
            "probabilities": probabilities,
            "total_variation_from_uniform": sum(abs(p - 1 / len(elites)) for p in probabilities)
            / 2,
        }


def novelty_screen(policy):
    exact = [name for name, ref in REFERENCES.items() if ref.identity == policy.identity]
    same_probe = [name for name, ref in REFERENCES.items() if signature(ref) == signature(policy)]
    return {
        "verdict": "known_reference" if exact else "unresolved",
        "exact_reference_matches": exact,
        "probe_matches": same_probe,
        "probe_sha256": digest(signature(policy)),
        "limitation": "Probe difference or syntax difference does not establish corpus novelty.",
    }


def corpus_manifest():
    return {
        "version": "reference-policies-v1",
        "status": "pilot_reference_set_only",
        "historical_cutoff": None,
        "sources": [
            {
                "name": name,
                "policy": p.to_object(),
                "sha256": p.identity,
                "provenance": "Original implementation of standard named heuristic",
                "license": "Apache-2.0",
            }
            for name, p in REFERENCES.items()
        ],
        "probe_sha256": digest(PROBES),
        "not_a_literature_corpus": True,
    }
