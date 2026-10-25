"""Audit an interrupted baseline journal offline, without inventing a response."""

import argparse
import io
import json
import random
from pathlib import Path

from .artifacts import digest, file_hash, write_json
from .backends import Proposal
from .baseline_runner import METHODS, run_condition
from .benchmark import make_suite, suite_record


class PendingResponse(Exception):
    """The journal records a request but no recoverable response."""


def audit_interruption(source, output):
    source, output = Path(source), Path(output)
    manifest = json.loads((source / "run_manifest.json").read_text())
    config = manifest["config"]
    for name, expected in manifest["input_files"].items():
        if file_hash(source / name) != expected:
            raise ValueError("input hash mismatch")
    if digest(json.loads((source / "train.json").read_text())) != digest(
        suite_record("train", config["per_family"])
    ):
        raise ValueError("training mismatch")
    original = (source / "events.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in original.splitlines()]
    if not rows or len(rows) % 2 != 1 or rows[-1]["phase"] != "started":
        raise ValueError("expected one unresolved trailing request")
    groups = []
    for index in range(0, len(rows), 2):
        started = rows[index]
        key = (started["seed"], started["method"])
        if started["phase"] != "started":
            raise ValueError("invalid journal ordering")
        if not groups or groups[-1][0] != key:
            groups.append((key, []))
        processed = rows[index + 1] if index + 1 < len(rows) else None
        if processed is not None and (
            processed["phase"] != "processed"
            or any(
                processed[k] != started[k]
                for k in ("seed", "method", "index", "request", "selection")
            )
        ):
            raise ValueError("request/response pairing mismatch")
        groups[-1][1].append((started, processed))
    order = []
    for seed in config["seeds"]:
        methods = list(METHODS)
        random.Random(seed + 909).shuffle(methods)
        order.extend((seed, method) for method in methods)
    if [key for key, _ in groups] != order[: len(groups)]:
        raise ValueError("condition order mismatch")
    journal, complete = io.StringIO(), []
    pending = None
    for (seed, method), pairs in groups:

        class Recorded:
            context = manifest["backend"]["options"]["num_ctx"]

            def __init__(self, records):
                self.position = 0
                self.records = records

            def identity(self):
                return manifest["backend"]

            def generate(self, system, prompt, schema, seed):
                started, processed = self.records[self.position]
                self.position += 1
                if started["request"] != {
                    "system": system,
                    "prompt": prompt,
                    "schema": schema,
                    "seed": seed,
                }:
                    raise ValueError("request replay mismatch")
                if processed is None:
                    raise PendingResponse
                return Proposal(
                    processed["response"],
                    processed["usage"],
                    processed["metadata"],
                    processed["provider_status"],
                )

        backend = Recorded(pairs)
        try:
            complete.append(
                run_condition(
                    config,
                    backend,
                    method,
                    seed,
                    make_suite("train", config["per_family"]),
                    journal,
                )
            )
        except PendingResponse:
            pending = pairs[-1][0]
        if backend.position != len(pairs):
            raise ValueError("unconsumed journal records")
    if pending is None or journal.getvalue() != original:
        raise ValueError("journal replay mismatch")
    saved = json.loads((source / "runs.json").read_text())
    if saved != complete:
        raise ValueError("completed condition mismatch")
    request = pending["request"]
    report = {
        "status": "interrupted_verified_prefix",
        "model_calls": 0,
        "started_requests": (len(rows) + 1) // 2,
        "recovered_responses": (len(rows) - 1) // 2,
        "unknown_responses": 1,
        "pending_request": pending,
        "pending_token_reservation": len((request["system"] + request["prompt"]).encode())
        + 512
        + config["max_output_tokens"],
        "pending_actual_usage": None,
        "usage_note": "Reservation is an accounting bound, not measured provider usage. Do not retry this request silently.",
        "completed_conditions": [{"method": r["method"], **r["summary"]} for r in complete],
        "source_files": {p.name: file_hash(p) for p in source.iterdir() if p.is_file()},
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "recovery-report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = audit_interruption(args.source, args.output)
    print(json.dumps({k: v for k, v in report.items() if k != "pending_request"}, indent=2))


if __name__ == "__main__":
    main()
