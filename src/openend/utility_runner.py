"""Training-only total-bin runner; offline CLI and saved-response replay."""

import argparse
import io
import json
import random
from pathlib import Path

from .artifacts import canonical, digest, file_hash, snapshot_source, source_manifest, write_json
from .backends import SYSTEM_PROMPT, Proposal
from .benchmark import evaluate, make_suite, suite_record
from .experiment import verify_artifacts
from .grammar import GRAMMAR_INSTRUCTIONS, policy_schema, validate_proposal_policy
from .policy import REFERENCES, Policy, mutate
from .utility_state import UtilityState

VERSION = "utility-runner-v1"
CONFIG = {
    "version": VERSION,
    "seeds": [42, 137, 2024],
    "calls": 40,
    "tokens": 60000,
    "max_output_tokens": 512,
    "per_family": 12,
}
SYSTEM = (
    SYSTEM_PROMPT.replace(
        "Parent fitness is\nmean(volume/count lower bound divided by bins used), higher is better.",
        "The objective is total training bins; lower is better.",
    )
    + GRAMMAR_INSTRUCTIONS
)
FATAL = {"missing_usage", "budget_overrun", "api_error", "model_changed", "unexpected_status"}


def validate_config(config):
    if set(config) != set(CONFIG) or config["version"] != VERSION:
        raise ValueError("invalid utility config")
    for key, high in (
        ("calls", 1000),
        ("tokens", 10000000),
        ("max_output_tokens", 2048),
        ("per_family", 100),
    ):
        if type(config[key]) is not int or not 1 <= config[key] <= high:
            raise ValueError(f"invalid {key}")
    seeds = config["seeds"]
    if (
        not isinstance(seeds, list)
        or not seeds
        or len(seeds) > 100
        or any(type(seed) is not int or not 0 <= seed < 2**32 for seed in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise ValueError("invalid seeds")


def parse(text):
    return validate_proposal_policy(Policy.from_text(text))


def snapshot(state):
    return {
        "cells": [
            [list(cell), p.to_object(), quality, list(sig)]
            for cell, (p, quality, sig) in sorted(state.archive.cells.items())
        ],
        "selected": state.selected(),
        "best_generated": state.best_generated,
        "valid_generated_count": state.generated_count,
    }


def condition(config, backend, seed, arm, train, journal):
    validate_config(config)
    if (
        arm not in ("uniform", "reference_weighted")
        or not train
        or any(not x.instance_id.startswith("train/") for x in train)
    ):
        raise ValueError("invalid arm or training data")
    state = UtilityState([(name, p, evaluate(p, train)) for name, p in REFERENCES.items()])
    selection_rng, model_rng = random.Random(seed + 111), random.Random(seed + 222)
    identity = backend.identity()
    expected_model = identity["model"] + "@" + identity["model_digest"]
    events, tokens, stop = [], 0, "call_limit"
    for index in range(config["calls"]):
        selection = state.request(selection_rng, arm == "reference_weighted")
        # Selection probabilities/arm labels are audit data, not model inputs.
        prompt = canonical({k: v for k, v in selection.items() if k != "selection"})
        reservation = (
            0
            if identity["kind"] == "offline_mutation"
            else len((SYSTEM + prompt).encode()) + 512 + config["max_output_tokens"]
        )
        if reservation > backend.context or tokens + reservation > config["tokens"]:
            stop = "context_admission" if reservation > backend.context else "token_admission"
            break
        request = {
            "system": SYSTEM,
            "prompt": prompt,
            "schema": policy_schema(),
            "seed": model_rng.randrange(2**31),
        }
        started = {
            "phase": "started",
            "arm": arm,
            "seed": seed,
            "index": index,
            "request": request,
            "selection": selection,
        }
        journal.write(canonical(started) + "\n")
        journal.flush()
        response = backend.generate(
            request["system"], request["prompt"], request["schema"], request["seed"]
        )
        usage = response.usage.get("total_tokens")
        status = response.status
        if type(usage) is not int or usage < 0:
            tokens += reservation
            status = "missing_usage"
        else:
            tokens += usage
        if status == "ok" and response.metadata.get("model") != expected_model:
            status = "model_changed"
        if tokens > config["tokens"]:
            status = "budget_overrun"
        if status not in {"ok", "truncated", "incomplete_response", *FATAL}:
            status = "unexpected_status"
        event = {
            "index": index,
            "request": request,
            "selection": selection,
            "reservation": reservation,
            "response": response.text,
            "usage": response.usage,
            "metadata": response.metadata,
            "provider_status": response.status,
            "status": status,
            "tokens_accounted": tokens,
        }
        if status == "ok":
            try:
                policy = parse(response.text)
            except (ValueError, TypeError, RecursionError):
                event["status"] = "invalid_policy"
            else:
                score = evaluate(policy, train)
                event.update(
                    policy=policy.to_object(), training=score, valid_ordinal=state.generated_count
                )
                state.observe(policy, score)
        event["state"] = snapshot(state)
        events.append(event)
        journal.write(canonical({"phase": "processed", "arm": arm, "seed": seed, **event}) + "\n")
        journal.flush()
        if event["status"] in FATAL:
            stop = event["status"]
            break
    return {
        "arm": arm,
        "seed": seed,
        "events": events,
        "stop": stop,
        "complete": stop == "call_limit" and len(events) == config["calls"],
        "selected": state.selected(),
        "tokens_accounted": tokens,
        "valid_policies": state.generated_count,
    }


class Offline:
    context = 8192

    def identity(self):
        return {
            "kind": "offline_mutation",
            "model": "tree-mutation",
            "model_digest": "utility-v1",
            "options": {"num_ctx": self.context},
        }

    def generate(self, system, prompt, schema, seed):
        parent = Policy.from_object(json.loads(prompt)["parent"])
        return Proposal(
            mutate(parent, random.Random(seed)),
            {"total_tokens": 0},
            {"model": "tree-mutation@utility-v1"},
        )


def execute(config, backend, train, journal):
    runs = []
    for seed in config["seeds"]:
        arms = ["uniform", "reference_weighted"]
        random.Random(seed + 909).shuffle(arms)
        for arm in arms:
            result = condition(config, backend, seed, arm, train, journal)
            runs.append(result)
            if result["stop"] in FATAL:
                return runs
    return runs


def run(config, backend, output, root):
    validate_config(config)
    output, root = Path(output), Path(root)
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "train.json", suite_record("train", config["per_family"]))
    (output / "protocol.md").write_bytes((root / "docs/utility-runner-v1-protocol.md").read_bytes())
    source = source_manifest(root)
    snapshot_source(root, source, output / "source.zip")
    manifest = {
        "experiment_kind": VERSION,
        "config": config,
        "backend": backend.identity(),
        "source": source,
        "status": "running",
        "input_files": {p.name: file_hash(p) for p in output.iterdir()},
    }
    write_json(output / "run_manifest.json", manifest)
    try:
        with (output / "events.jsonl").open("x", encoding="utf-8") as journal:
            runs = execute(config, backend, make_suite("train", config["per_family"]), journal)
        write_json(output / "runs.json", runs)
        manifest["status"] = (
            "completed"
            if len(runs) == 2 * len(config["seeds"]) and all(r["complete"] for r in runs)
            else "incomplete"
        )
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
    return {
        "status": manifest["status"],
        "runs": [{k: v for k, v in r.items() if k != "events"} for r in runs],
    }


def replay(output):
    output = Path(output)
    verify_artifacts(output)
    manifest = json.loads((output / "run_manifest.json").read_text())
    if manifest["experiment_kind"] != VERSION or manifest["status"] not in (
        "completed",
        "incomplete",
    ):
        raise ValueError("not finalized utility run")
    config = manifest["config"]
    validate_config(config)
    if digest(json.loads((output / "train.json").read_text())) != digest(
        suite_record("train", config["per_family"])
    ):
        raise ValueError("training mismatch")
    saved = json.loads((output / "runs.json").read_text())
    events = [event for r in saved for event in r["events"]]

    class Recorded:
        context = manifest["backend"]["options"]["num_ctx"]
        position = 0

        def identity(self):
            return manifest["backend"]

        def generate(self, system, prompt, schema, seed):
            request = {"system": system, "prompt": prompt, "schema": schema, "seed": seed}
            event = events[self.position]
            self.position += 1
            if request != event["request"]:
                raise ValueError("request mismatch")
            return Proposal(
                event["response"], event["usage"], event["metadata"], event["provider_status"]
            )

    backend, journal = Recorded(), io.StringIO()
    actual = execute(config, backend, make_suite("train", config["per_family"]), journal)
    if (
        actual != saved
        or backend.position != len(events)
        or journal.getvalue() != (output / "events.jsonl").read_text(encoding="utf-8")
    ):
        raise ValueError("state or journal mismatch")
    completed = len(actual) == 2 * len(config["seeds"]) and all(r["complete"] for r in actual)
    if completed != (manifest["status"] == "completed"):
        raise ValueError("completion mismatch")
    return {"replay": "matched", "attempts": len(events), "model_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("offline", "replay"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            replay(args.output)
            if args.command == "replay"
            else run(CONFIG, Offline(), args.output, Path.cwd()),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
