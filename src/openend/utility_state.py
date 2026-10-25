"""Prospective bin-count objective shared by archive, prompts and output selection.

This state is separate from historical fitness-based experiment/replay code.
"""

from .artifacts import canonical
from .policy import Policy
from .search import PROBES, Archive


class UtilityState:
    def __init__(self, references, resolution=6, panel=PROBES):
        if not references:
            raise ValueError("references required")
        self.archive = Archive(resolution, panel)
        self.reference = None
        self.best_generated = None
        self.generated_count = 0
        for name, policy, score in references:
            record = self.record(policy, score, name)
            self.archive.insert(policy, -record["total_bins"])
            if self.reference is None or record["total_bins"] < self.reference["total_bins"]:
                self.reference = record

    @staticmethod
    def record(policy, score, origin):
        bins = score["total_bins"]
        if type(bins) is not int or bins < 1:
            raise ValueError("positive integer training bins required")
        return {"policy": policy.to_object(), "total_bins": bins, "origin": origin}

    def observe(self, policy, score):
        record = self.record(policy, score, self.generated_count)
        self.generated_count += 1
        self.archive.insert(policy, -record["total_bins"])
        if self.best_generated is None or record["total_bins"] < self.best_generated["total_bins"]:
            self.best_generated = record

    def request(self, rng, weighted):
        parent, quality, _ = self.archive.select(rng, sparse=weighted)
        return {
            "parent": parent.to_object(),
            "training_total_bins": -quality,
            "objective": "minimize_total_training_bins",
            "selection": self.archive.selection_diagnostics(sparse=weighted),
        }

    def selected(self):
        generated = self.best_generated
        fallback = generated is None or generated["total_bins"] >= self.reference["total_bins"]
        record = self.reference if fallback else generated
        # Return detached JSON data so callers cannot mutate retained selection state.
        import json

        return json.loads(canonical({**record, "used_fallback": fallback}))

    def selected_policy(self):
        return Policy.from_object(self.selected()["policy"])
