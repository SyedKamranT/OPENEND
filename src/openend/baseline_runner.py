"""Budgeted, training-only baseline adapters with full request/state replay."""

import argparse
import json
import random
from pathlib import Path

from .artifacts import canonical, digest, file_hash, snapshot_source, source_manifest, write_json
from .backends import SYSTEM_PROMPT, Proposal
from .baseline_state import EohState, FunsearchState, candidate
from .benchmark import evaluate, make_suite, reference_scores, successful, suite_record
from .experiment import verify_artifacts
from .grammar import GRAMMAR_INSTRUCTIONS, policy_schema, validate_proposal_policy
from .local import LocalBackend
from .policy import REFERENCES, Policy

METHODS = ("independent", "eoh_json", "funsearch_json")
FATAL = {"missing_usage", "budget_overrun", "api_error", "model_changed"}
PROMPT_VERSION = "baseline-json-v1"
OPERATOR_TASKS = {
    "i1": "Create an initial heuristic and its short mechanism description.",
    "e1": "Create a heuristic with a different form from the supplied parents.",
    "e2": "Identify a common mechanism in the parents and derive a different heuristic from it.",
    "m1": "Modify the supplied heuristic's mechanism into a different form.",
    "m2": "Identify and change the supplied heuristic's parameter settings.",
}


def load_config(path):
    config = json.loads(Path(path).read_text())
    required = {
        "version",
        "model",
        "seeds",
        "calls",
        "tokens",
        "max_output_tokens",
        "per_family",
        "population_size",
        "islands",
        "reset_attempts",
    }
    if set(config) != required or config["version"] != PROMPT_VERSION:
        raise ValueError("invalid baseline config")
    for key, low, high in (
        ("calls", 1, 1000),
        ("tokens", 1, 10000000),
        ("max_output_tokens", 64, 2048),
        ("per_family", 1, 100),
        ("population_size", 2, 100),
        ("islands", 2, 100),
        ("reset_attempts", 1, 10000),
    ):
        if type(config[key]) is not int or not low <= config[key] <= high:
            raise ValueError(f"invalid {key}")
    if (
        not isinstance(config["seeds"], list)
        or not config["seeds"]
        or any(type(x) is not int or not 0 <= x < 2**32 for x in config["seeds"])
        or len(set(config["seeds"])) != len(config["seeds"])
    ):
        raise ValueError("invalid seeds")
    return config


def request_for(method, state_request):
    schema = policy_schema()
    system = SYSTEM_PROMPT + GRAMMAR_INSTRUCTIONS
    system = system.replace("Return a small variation of the supplied parent.", "")
    system = system.replace(
        "Parent fitness is\nmean(volume/count lower bound divided by bins used), higher is better.",
        "Training bin count is the objective; lower is better.",
    )
    # Remove the legacy single-parent objective to avoid contradicting batch prompts.
    system = system.replace(
        "Improve the given parent using a nontrivial small variation.",
        "Follow the supplied search operator.",
    )
    parents = [
        {"policy": p["policy"], "training_bins": p["objective"], "thought": p["thought"]}
        for p in state_request["parents"]
    ]
    payload = {
        "prompt_version": PROMPT_VERSION,
        "parents": parents,
        "objective": "minimize total bins on the four training families",
    }
    if method == "eoh_json":
        system = system.replace(
            "exactly one field: expression", "exactly two fields: thought and expression"
        )
        system = system.replace(
            "No Python, prose, or code fences.",
            "No Python or code fences. Put a short mechanism description in thought.",
        )
        schema["properties"]["thought"] = {"type": "string", "minLength": 1, "maxLength": 400}
        schema["required"].append("thought")
        payload["operator"] = state_request["operator"]
        payload["task"] = OPERATOR_TASKS[state_request["operator"]]
    elif method == "funsearch_json":
        payload["versions"] = [{"version": i, **parent} for i, parent in enumerate(parents)]
        payload["task"] = (
            "Propose the next improved expression version, following the scored examples."
        )
    else:
        payload["task"] = (
            "Independently propose an improved scoring policy from this fixed reference."
        )
    return system, canonical(payload), schema


def parse_response(text, method):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate response field")
            value[key] = item
        return value

    if not isinstance(text, str) or len(text.encode()) > 16384:
        raise ValueError("invalid response")
    value = json.loads(text, object_pairs_hook=unique)
    expected = {"expression", "thought"} if method == "eoh_json" else {"expression"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("invalid response fields")
    thought = value.get("thought", "")
    if method == "eoh_json" and (not isinstance(thought, str) or not 1 <= len(thought) <= 400):
        raise ValueError("invalid thought")
    policy = validate_proposal_policy(Policy.from_object({"expression": value["expression"]}))
    return policy, thought


def run_condition(config, backend, method, seed, train, journal):
    if method not in METHODS or any(not x.instance_id.startswith("train/") for x in train):
        raise ValueError("invalid method or nontraining data")
    refs = reference_scores(train)
    best_name = min(refs, key=lambda k: refs[k]["total_bins"])
    initial = candidate(REFERENCES[best_name], evaluate(REFERENCES[best_name], train), best_name)
    state = (
        EohState(config["population_size"], seed + 101)
        if method == "eoh_json"
        else FunsearchState(config["islands"], config["reset_attempts"], initial, seed + 101)
        if method == "funsearch_json"
        else None
    )
    model_rng, events, tokens = random.Random(seed + 202), [], 0
    stop = "call_limit"
    identity = backend.identity()
    expected_model = identity["model"] + "@" + identity["model_digest"]
    for index in range(config["calls"]):
        try:
            selection = (
                state.request() if state else {"operator": "independent", "parents": [initial]}
            )
        except ValueError as exc:
            stop = str(exc)
            break
        system, prompt, schema = request_for(method, selection)
        reservation = len((system + prompt).encode()) + 512 + config["max_output_tokens"]
        if reservation > backend.context or tokens + reservation > config["tokens"]:
            stop = "context_admission" if reservation > backend.context else "token_admission"
            break
        request = {
            "system": system,
            "prompt": prompt,
            "schema": schema,
            "seed": model_rng.randrange(2**31),
        }
        started = {
            "phase": "started",
            "method": method,
            "seed": seed,
            "index": index,
            "request": request,
            "selection": selection,
        }
        journal.write(canonical(started) + "\n")
        journal.flush()
        response = backend.generate(system, prompt, schema, request["seed"])
        status = response.status
        usage = response.usage.get("total_tokens")
        if type(usage) is not int or usage < 0:
            tokens += reservation
            status = "missing_usage"
        else:
            tokens += usage
        if status == "ok" and response.metadata.get("model") != expected_model:
            status = "model_changed"
        if tokens > config["tokens"]:
            status = "budget_overrun"
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
        proposal = None
        if status == "ok":
            try:
                policy, thought = parse_response(response.text, method)
                score = evaluate(policy, train)
                proposal = candidate(policy, score, thought)
                event.update(
                    candidate=proposal,
                    training=score,
                    training_utility_success=successful(score, refs),
                )
            except (ValueError, TypeError, RecursionError):
                event["status"] = "invalid_policy"
        event["state"] = state.observe(selection, proposal) if state else None
        events.append(event)
        journal.write(
            canonical({"phase": "processed", "method": method, "seed": seed, **event}) + "\n"
        )
        journal.flush()
        print(f"{method} seed={seed} call={index + 1} status={event['status']}", flush=True)
        if event["status"] in FATAL:
            stop = event["status"]
            break
    valid = [e for e in events if "candidate" in e]
    best = min(valid, key=lambda e: (e["candidate"]["objective"], e["index"]), default=None)
    selected = (
        best["candidate"]
        if best and best["candidate"]["objective"] < initial["objective"]
        else initial
    )
    return {
        "method": method,
        "seed": seed,
        "events": events,
        "stop_reason": stop,
        "complete": stop == "call_limit" and len(events) == config["calls"],
        "summary": {
            "calls": len(events),
            "valid_policies": len(valid),
            "tokens_accounted": tokens,
            "best_generated_train_bins": best["candidate"]["objective"] if best else None,
            "selected_train_bins": selected["objective"],
            "selected_policy": selected["policy"],
            "reference": best_name,
            "used_fallback": selected is initial,
            "utility_successes": sum(e["training_utility_success"] for e in valid),
            "wall_seconds": sum(e["metadata"].get("wall_seconds", 0) for e in events),
        },
    }


def run(config, backend, output, root, protocol_path=None):
    output, root = Path(output), Path(root)
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "train.json", suite_record("train", config["per_family"]))
    (output / "protocol.md").write_bytes(
        (
            Path(protocol_path) if protocol_path else root / "docs/baseline-adapters-v1-protocol.md"
        ).read_bytes()
    )
    (output / "upstream_manifest.json").write_bytes(
        (root / "data/baselines/upstream-v1/manifest.json").read_bytes()
    )
    source = source_manifest(root)
    snapshot_source(root, source, output / "source.zip")
    manifest = {
        "experiment_kind": PROMPT_VERSION,
        "config": config,
        "source": source,
        "backend": backend.identity(),
        "status": "running",
        "input_files": {p.name: file_hash(p) for p in output.iterdir()},
    }
    write_json(output / "run_manifest.json", manifest)
    train = make_suite("train", config["per_family"])
    runs = []
    try:
        with (output / "events.jsonl").open("x", encoding="utf-8") as journal:
            for seed in config["seeds"]:
                methods = list(METHODS)
                random.Random(seed + 909).shuffle(methods)
                for method in methods:
                    result = run_condition(config, backend, method, seed, train, journal)
                    runs.append(result)
                    write_json(output / "runs.json", runs)
                    if result["stop_reason"] in FATAL:
                        break
                if runs[-1]["stop_reason"] in FATAL:
                    break
        manifest["status"] = (
            "completed"
            if (
                len(runs) == len(METHODS) * len(config["seeds"])
                and all(r["complete"] for r in runs)
            )
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
        "runs": [{"method": r["method"], **r["summary"]} for r in runs],
    }


def replay(output):
    import io

    output = Path(output)
    verify_artifacts(output)
    manifest = json.loads((output / "run_manifest.json").read_text())
    if manifest["experiment_kind"] != PROMPT_VERSION or manifest["status"] not in (
        "completed",
        "incomplete",
    ):
        raise ValueError("not finalized baseline adapters")
    config = manifest["config"]
    saved = json.loads((output / "runs.json").read_text())
    expected_order = []
    for seed in config["seeds"]:
        methods = list(METHODS)
        random.Random(seed + 909).shuffle(methods)
        expected_order.extend((seed, method) for method in methods)
    if [(r["seed"], r["method"]) for r in saved] != expected_order[: len(saved)]:
        raise ValueError("condition order mismatch")
    complete = len(saved) == len(expected_order) and all(r["complete"] for r in saved)
    if (manifest["status"] == "completed") != complete:
        raise ValueError("completion mismatch")
    if digest(json.loads((output / "train.json").read_text())) != digest(
        suite_record("train", config["per_family"])
    ):
        raise ValueError("training mismatch")
    journal = io.StringIO()
    calls = 0
    for original in saved:

        class Recorded:
            context = manifest["backend"]["options"]["num_ctx"]

            def __init__(self, events):
                self.events, self.position = events, 0

            def identity(self):
                return manifest["backend"]

            def generate(self, system, prompt, schema, seed):
                event = self.events[self.position]
                self.position += 1
                if event["request"] != {
                    "system": system,
                    "prompt": prompt,
                    "schema": schema,
                    "seed": seed,
                }:
                    raise ValueError("request mismatch")
                return Proposal(
                    event["response"], event["usage"], event["metadata"], event["provider_status"]
                )

        backend = Recorded(original["events"])
        actual = run_condition(
            config,
            backend,
            original["method"],
            original["seed"],
            make_suite("train", config["per_family"]),
            journal,
        )
        if actual != original or backend.position != len(original["events"]):
            raise ValueError("state replay mismatch")
        calls += backend.position
    if journal.getvalue() != (output / "events.jsonl").read_text(encoding="utf-8"):
        raise ValueError("journal mismatch")
    return {"replay": "matched", "calls": calls, "model_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "replay"))
    parser.add_argument("output", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/baseline_adapters_v1.json"))
    args = parser.parse_args()
    if args.command == "replay":
        result = replay(args.output)
    else:
        config = load_config(args.config)
        backend = LocalBackend(config["model"], config["max_output_tokens"], structured=True)
        try:
            result = run(config, backend, args.output, Path.cwd())
        finally:
            backend._request("generate", {"model": config["model"], "keep_alive": 0})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
