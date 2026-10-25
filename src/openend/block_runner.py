"""Offline development-block engineering trial with selection freeze and replay."""

import argparse
import io
import json
from pathlib import Path

from .artifacts import digest, file_hash, snapshot_source, source_manifest, write_json
from .backends import Proposal
from .benchmark import evaluate
from .development_blocks import record, suite
from .experiment import verify_artifacts
from .policy import Policy
from .utility_planning import summarize
from .utility_runner import CONFIG, Offline, execute

PLAN = {"master_seed": 20261014, "blocks": 8, "search": {**CONFIG, "seeds": [42, 137], "calls": 20}}


def evaluation(plan, blocks):
    rows = []
    for block, runs in enumerate(blocks):
        data = suite(plan["master_seed"], block, "development_eval", plan["search"]["per_family"])
        for seed in plan["search"]["seeds"]:
            paired = {}
            for result in (r for r in runs if r["seed"] == seed):
                policy = Policy.from_object(result["selected"]["policy"])
                paired[result["arm"]] = evaluate(policy, data)
            rows.append(
                {
                    "block": block,
                    "run": seed,
                    "complete": True,
                    "difference": paired["uniform"]["total_bins"]
                    - paired["reference_weighted"]["total_bins"],
                    "scores": paired,
                }
            )
    return {"pairs": rows, "summary": summarize(rows), "scope": "development_only"}


def selections(blocks):
    return [
        [{"arm": r["arm"], "seed": r["seed"], "selected": r["selected"]} for r in runs]
        for runs in blocks
    ]


def run(output, root, plan=None):
    plan = PLAN if plan is None else plan
    output, root = Path(output), Path(root)
    output.mkdir(parents=True, exist_ok=False)
    for block in range(plan["blocks"]):
        for role in ("train", "development_eval"):
            write_json(
                output / f"{block}-{role}.json",
                record(plan["master_seed"], block, role, plan["search"]["per_family"]),
            )
    (output / "protocol.md").write_bytes(
        (root / "docs/development-blocks-v1-protocol.md").read_bytes()
    )
    source = source_manifest(root)
    snapshot_source(root, source, output / "source.zip")
    backend = Offline()
    manifest = {
        "experiment_kind": "development-blocks-offline-v1",
        "status": "running",
        "plan": plan,
        "source": source,
        "backend": backend.identity(),
        "input_files": {p.name: file_hash(p) for p in output.iterdir()},
    }
    write_json(output / "run_manifest.json", manifest)
    blocks = []
    try:
        for block in range(plan["blocks"]):
            train = suite(plan["master_seed"], block, "train", plan["search"]["per_family"])
            with (output / f"{block}-events.jsonl").open("x", encoding="utf-8") as journal:
                runs = execute(plan["search"], backend, train, journal)
            blocks.append(runs)
            write_json(output / "runs.json", blocks)
            if len(runs) != 2 * len(plan["search"]["seeds"]) or not all(
                r["complete"] for r in runs
            ):
                raise ValueError("incomplete block")
        frozen = selections(blocks)
        write_json(output / "selected.json", {"policies": frozen, "sha256": digest(frozen)})
        manifest["selection_file_sha256_before_evaluation"] = file_hash(output / "selected.json")
        write_json(output / "run_manifest.json", manifest)
        results = evaluation(plan, blocks)
        write_json(output / "evaluation.json", results)
        if (
            file_hash(output / "selected.json")
            != manifest["selection_file_sha256_before_evaluation"]
        ):
            raise ValueError("selections changed during evaluation")
        manifest["status"] = "completed"
    except BaseException:
        manifest["status"] = "interrupted_or_failed"
        raise
    finally:
        manifest["output_files"] = {
            p.name: file_hash(p)
            for p in output.iterdir()
            if p.name not in {*manifest["input_files"], "run_manifest.json"}
        }
        write_json(output / "run_manifest.json", manifest)
    return results["summary"]


def replay(output):
    output = Path(output)
    verify_artifacts(output)
    manifest = json.loads((output / "run_manifest.json").read_text())
    if (
        manifest["experiment_kind"] != "development-blocks-offline-v1"
        or manifest["status"] != "completed"
    ):
        raise ValueError("not complete block study")
    plan = manifest["plan"]
    blocks = json.loads((output / "runs.json").read_text())
    if len(blocks) != plan["blocks"]:
        raise ValueError("block count mismatch")
    calls = 0
    for block, runs in enumerate(blocks):
        for role in ("train", "development_eval"):
            saved = json.loads((output / f"{block}-{role}.json").read_text())
            if digest(saved) != digest(
                record(plan["master_seed"], block, role, plan["search"]["per_family"])
            ):
                raise ValueError("dataset mismatch")

        class Recorded:
            context = 8192

            def __init__(self, records):
                self.events = [e for r in records for e in r["events"]]
                self.position = 0

            def identity(self):
                return manifest["backend"]

            def generate(self, system, prompt, schema, seed):
                request = {"system": system, "prompt": prompt, "schema": schema, "seed": seed}
                event = self.events[self.position]
                self.position += 1
                if request != event["request"]:
                    raise ValueError("request mismatch")
                return Proposal(
                    event["response"], event["usage"], event["metadata"], event["provider_status"]
                )

        backend, journal = Recorded(runs), io.StringIO()
        actual = execute(
            plan["search"],
            backend,
            suite(plan["master_seed"], block, "train", plan["search"]["per_family"]),
            journal,
        )
        if (
            actual != runs
            or backend.position != len(backend.events)
            or journal.getvalue() != (output / f"{block}-events.jsonl").read_text(encoding="utf-8")
        ):
            raise ValueError("block replay mismatch")
        calls += backend.position
    frozen = json.loads((output / "selected.json").read_text())
    if (
        frozen != {"policies": selections(blocks), "sha256": digest(selections(blocks))}
        or file_hash(output / "selected.json")
        != manifest["selection_file_sha256_before_evaluation"]
    ):
        raise ValueError("selection commitment mismatch")
    if evaluation(plan, blocks) != json.loads((output / "evaluation.json").read_text()):
        raise ValueError("evaluation mismatch")
    return {"replay": "matched", "attempts": calls, "model_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "replay"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            replay(args.output) if args.command == "replay" else run(args.output, Path.cwd()),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
