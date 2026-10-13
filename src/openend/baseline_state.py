"""Serial shared-JSON adaptations of pinned EoH/FunSearch search state.

These are explicit adaptations, not native Python reproductions. Source/license
provenance is in data/baselines/upstream-v1 and docs/baseline-fidelity-v1.md.
"""

import copy
import random

from .artifacts import canonical, digest
from .baseline_mechanics import (
    eoh_parents,
    eoh_survivors,
    funsearch_length_probabilities,
    funsearch_reduced_score,
    funsearch_scores,
    funsearch_signature,
    funsearch_temperature,
    softmax,
)


def candidate(policy, score, thought=""):
    return {
        "policy": policy.to_object(),
        "id": policy.identity,
        "objective": score["total_bins"],
        "scores": funsearch_scores(score),
        "thought": thought,
    }


class EohState:
    """Two population-sized initialization batches, then e1/e2/m1/m2 batches."""

    def __init__(self, size, seed):
        self.size, self.rng = size, random.Random(seed)
        self.population, self.pending = [], []
        self.attempts = 0

    def request(self):
        if self.attempts < 2 * self.size:
            return {"operator": "i1", "parents": []}
        if not self.population:
            raise ValueError("empty_eoh_population")
        operator = ("e1", "e2", "m1", "m2")[(self.attempts // self.size - 2) % 4]
        count = 2 if operator.startswith("e") else 1
        parents = eoh_parents(self.population, count, self.rng)
        return {"operator": operator, "parents": copy.deepcopy(parents)}

    def observe(self, request, proposal):
        if proposal is not None:
            self.pending.append(proposal)
        self.attempts += 1
        # No within-batch feedback: all offspring in a batch use the same population.
        if self.attempts >= 2 * self.size and self.attempts % self.size == 0:
            self.population = eoh_survivors(self.population + self.pending, self.size)
            self.pending = []
        return {
            "population": [x["id"] for x in self.population],
            "pending": [x["id"] for x in self.pending],
            "attempts": self.attempts,
        }


class FunsearchState:
    """Island/cluster model; attempt-based reset and Python RNG are adaptations."""

    def __init__(self, islands, reset_attempts, initial, seed):
        self.rng = random.Random(seed)
        self.reset_attempts, self.attempts = reset_attempts, 0
        self.islands = [self.new_island() for _ in range(islands)]
        for island in self.islands:
            self.register(island, copy.deepcopy(initial))

    @staticmethod
    def new_island():
        return {"clusters": {}, "registrations": 0, "best": None}

    @staticmethod
    def register(island, proposal):
        key = funsearch_signature(proposal["scores"])
        island["clusters"].setdefault(key, []).append(proposal)
        island["registrations"] += 1
        if island["best"] is None or proposal["objective"] < island["best"]["objective"]:
            island["best"] = proposal

    def request(self):
        index = self.rng.randrange(len(self.islands))
        island = self.islands[index]
        clusters = list(island["clusters"].values())
        temperature = funsearch_temperature(island["registrations"])
        probabilities = softmax(
            [funsearch_reduced_score(c[0]["scores"]) for c in clusters], temperature
        )
        selected = self.rng.choices(
            range(len(clusters)), weights=probabilities, k=min(2, len(clusters))
        )
        parents = []
        for i in selected:
            cluster = clusters[i]
            lengths = [len(canonical(x["policy"])) for x in cluster]
            parents.append(
                self.rng.choices(cluster, weights=funsearch_length_probabilities(lengths))[0]
            )
        # Low score (worse) first, high score (better) last.
        parents.sort(key=lambda p: funsearch_reduced_score(p["scores"]))
        return {
            "operator": "versioned_improvement",
            "island": index,
            "temperature": temperature,
            "cluster_probabilities": probabilities,
            "sampled_clusters": selected,
            "parents": copy.deepcopy(parents),
        }

    def observe(self, request, proposal):
        if proposal is not None:
            self.register(self.islands[request["island"]], proposal)
        self.attempts += 1
        resets = []
        if self.attempts % self.reset_attempts == 0:
            noisy = [
                (funsearch_reduced_score(x["best"]["scores"]) + self.rng.gauss(0, 1) * 1e-6, i)
                for i, x in enumerate(self.islands)
            ]
            order = [i for _, i in sorted(noisy)]
            count = len(order) // 2
            for target in order[:count]:
                founder = self.rng.choice(order[count:])
                best = copy.deepcopy(self.islands[founder]["best"])
                self.islands[target] = self.new_island()
                self.register(self.islands[target], best)
                resets.append(
                    {"island": target, "founder_island": founder, "policy_id": best["id"]}
                )
        state = [
            {
                "registrations": x["registrations"],
                "best": x["best"]["id"],
                "clusters": [[list(k), [p["id"] for p in v]] for k, v in x["clusters"].items()],
            }
            for x in self.islands
        ]
        return {
            "attempts": self.attempts,
            "resets": resets,
            "islands": state,
            "state_sha256": digest(state),
        }
