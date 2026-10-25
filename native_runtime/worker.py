"""Runs only inside the restricted native container; never import on the host."""

import json
import sys

import numpy as np


def evaluate(payload):
    scope = {"np": np}
    # Candidate code is untrusted. Isolation is enforced by the external container host.
    exec(payload["code"], scope)  # noqa: S102 - container-only worker
    scorer = scope[payload["function"]]
    rows = []
    for instance in payload["instances"]:
        bins = np.full(len(instance["items"]), instance["capacity"], dtype=float)
        assignments = []
        for item in instance["items"]:
            feasible = np.where(bins >= item)[0]
            scores = np.asarray(scorer(item, bins[feasible].copy()))
            if scores.shape != feasible.shape or not np.all(np.isfinite(scores)):
                raise ValueError("invalid score vector")
            selected = int(feasible[np.argmax(scores)])
            bins[selected] -= item
            assignments.append(selected)
        # Canonicalize labels in arrival order for independent host certificate checks.
        labels = {}
        assignments = [labels.setdefault(i, len(labels)) for i in assignments]
        rows.append({"instance_id": instance["instance_id"], "assignments": assignments})
    return {"instances": rows}


if __name__ == "__main__":
    try:
        payload = json.loads(sys.stdin.buffer.read(65537))
        print(json.dumps(evaluate(payload), allow_nan=False))
    except BaseException as exc:  # noqa: BLE001 - serialize candidate termination inside container
        print(json.dumps({"error": type(exc).__name__}))
        raise SystemExit(1)
