"""Budgeted serial agent coordination and matched end-to-end baseline conditions."""

import argparse
import io
import json
import random
from datetime import UTC, datetime
from pathlib import Path

from .agents import (
    CRITIC_SCHEMA,
    CRITIC_SYSTEM,
    POLICY_SYSTEM,
    cell_for,
    parse_critique,
    select_target,
    target_library,
)
from .artifacts import canonical, digest, file_hash, snapshot_source, source_manifest, write_json
from .backends import Proposal
from .benchmark import Instance, evaluate, make_suite, reference_scores, successful, suite_record
from .corpus import load as load_corpus
from .corpus import search as retrieve
from .equivalence import certify
from .experiment import verify_artifacts
from .grammar import policy_schema
from .local import LocalBackend
from .policy import REFERENCES, InvalidPolicy, Policy
from .probes import build_panel_record, panel_from_record, saved_panel
from .search import Archive

CONDITIONS = ("independent", "retrieval", "coordinator_uniform", "coordinator_targeted")
DEFAULT_QUERY = "online bin packing heuristic evolution"
FATAL = {"api_error", "missing_usage", "model_changed", "budget_overrun"}


def load_config(path):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "version",
        "purpose",
        "model",
        "seeds",
        "calls_per_condition",
        "tokens_per_condition",
        "max_output_tokens",
        "per_family",
        "grid_resolution",
        "minimum_improvement",
        "probe_panel",
        "corpus_sha256",
    }
    if (
        not isinstance(config, dict)
        or set(config) != required
        or config["purpose"] != "engineering_pilot"
    ):
        raise ValueError("invalid coordinator configuration")
    for key, low, high in (
        ("calls_per_condition", 3, 300),
        ("tokens_per_condition", 1, 1000000),
        ("max_output_tokens", 16, 8192),
        ("per_family", 1, 100),
        ("grid_resolution", 2, 20),
    ):
        if type(config[key]) is not int or not low <= config[key] <= high:
            raise ValueError(f"invalid {key}")
    if config["calls_per_condition"] % 3:
        raise ValueError("call allowance must contain complete three-role cycles")
    seeds = config["seeds"]
    if (
        not isinstance(seeds, list)
        or not seeds
        or any(type(x) is not int or not 0 <= x < 2**32 for x in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise ValueError("invalid seeds")
    if (
        type(config["minimum_improvement"]) not in (int, float)
        or not 0 < config["minimum_improvement"] < 1
    ):
        raise ValueError("invalid improvement margin")
    return config


def _journal(handle, event):
    handle.write(canonical(event) + "\n")
    handle.flush()


def _compact_score(score):
    return {key: score[key] for key in ("fitness", "total_bins", "family_bins")}


def run_condition(config, backend, seed, condition, train, panel, corpus_path, journal):
    archive = Archive(config["grid_resolution"], panel)
    reference_evaluations = {name: evaluate(policy, train) for name, policy in REFERENCES.items()}
    for name, policy in REFERENCES.items():
        archive.insert(policy, reference_evaluations[name]["fitness"])
    best_name = min(
        reference_evaluations, key=lambda name: reference_evaluations[name]["total_bins"]
    )
    fixed_parent = REFERENCES[best_name]
    library = target_library(panel, config["grid_resolution"])
    parent_rng, model_rng, target_rng = (random.Random(seed + offset) for offset in (111, 333, 444))
    coordinated = condition.startswith("coordinator_")
    visits, events, tokens, state = {}, [], 0, {}
    stop_reason, usage_complete = "call_limit", True
    identity = backend.identity()
    expected_model = identity["model"] + "@" + identity["model_digest"]
    for index in range(config["calls_per_condition"]):
        phase = index % 3 if coordinated else 0
        role = ("generator", "critic", "recombiner")[phase]
        if phase == 0:
            if coordinated:
                parent, fitness, _ = archive.select(parent_rng, sparse=False)
                donors = [
                    entry[0]
                    for entry in archive.cells.values()
                    if entry[0].identity != parent.identity
                ]
                donor = parent_rng.choice(donors) if donors else parent
            else:
                parent, fitness, donor = (
                    fixed_parent,
                    reference_evaluations[best_name]["fitness"],
                    fixed_parent,
                )
            target = (
                select_target(library, archive, visits, target_rng, parent)
                if condition == "coordinator_targeted"
                else None
            )
            state = {
                "parent": parent,
                "fitness": fitness,
                "donor": donor,
                "target": target,
                "critique": None,
                "proposal": None,
            }
        target_prompt = (
            {key: value for key, value in state["target"].items() if key != "witness_policy"}
            if state["target"]
            else None
        )
        query = (state["critique"] or {}).get("prior_art_query") or DEFAULT_QUERY
        evidence = retrieve(corpus_path, query, top_k=2) if condition != "independent" else None
        leads = (
            [
                {key: hit[key] for key in ("id", "title", "note", "source_url", "evidence_scope")}
                for hit in evidence["hits"]
            ]
            if evidence
            else []
        )
        payload = {
            "parent": state["parent"].to_object(),
            "training_fitness": state["fitness"],
            "target": target_prompt,
            "source_leads": leads,
        }
        if phase:
            proposal = state["proposal"]
            payload["proposal"] = proposal["policy"] if proposal else state["parent"].to_object()
            payload["training_feedback"] = (
                _compact_score(proposal["train"])
                if proposal
                else {"status": "generation_invalid_use_parent"}
            )
            payload["known_mechanism_check"] = (
                {key: proposal["verification"].get(key) for key in ("verdict", "matches", "reason")}
                if proposal
                else None
            )
        if role == "recombiner":
            payload.update(donor=state["donor"].to_object(), critique=state["critique"])
        system, schema = (
            (CRITIC_SYSTEM, CRITIC_SCHEMA) if role == "critic" else (POLICY_SYSTEM, policy_schema())
        )
        if role == "recombiner":
            system += "\nAct as the recombination agent: combine useful parts of proposal and donor while critically using the revision advice."
        prompt = canonical(payload)
        reservation = len((system + prompt).encode()) + 512 + config["max_output_tokens"]
        if reservation > backend.context:
            stop_reason = "context_admission_limit"
            break
        if tokens + reservation > config["tokens_per_condition"]:
            stop_reason = "token_admission_limit"
            break
        request = {
            "system": system,
            "prompt": prompt,
            "format": schema,
            "seed": model_rng.randrange(2**31),
        }
        event_id = f"{seed}/{condition}/{index:04}"
        _journal(
            journal,
            {
                "phase": "request_started",
                "event_id": event_id,
                "role": role,
                "reservation": reservation,
                "request": request,
            },
        )
        result = backend.generate(system, prompt, schema, request["seed"])
        event = {
            "event_id": event_id,
            "role": role,
            "request": request,
            "reservation": reservation,
            "provider_status": result.status,
            "status": result.status,
            "response_text": result.text,
            "usage": result.usage,
            "response_metadata": result.metadata,
            "retrieval": evidence,
            "target": state["target"],
        }
        usage = result.usage.get("total_tokens")
        if type(usage) is not int or usage < 0:
            usage_complete = False
            tokens += reservation
            if event["status"] == "ok":
                event["status"] = "missing_usage"
        else:
            tokens += usage
        if event["status"] == "ok" and result.metadata.get("model") != expected_model:
            event["status"] = "model_changed"
        if tokens > config["tokens_per_condition"]:
            event["status"] = "budget_overrun"
        event["tokens_accounted_so_far"] = tokens
        if event["status"] == "ok":
            try:
                if role == "critic":
                    state["critique"] = parse_critique(result.text)
                    event["critique"] = state["critique"]
                else:
                    policy = Policy.from_text(result.text)
                    score = evaluate(policy, train)
                    event.update(
                        policy=policy.to_object(),
                        candidate_id=policy.identity,
                        train=score,
                        verification=certify(policy),
                    )
                    event["target_reached"] = (
                        list(cell_for(policy, panel, archive.resolution)) == state["target"]["cell"]
                        if state["target"]
                        else None
                    )
                    archive.insert(policy, score["fitness"])
                    if role == "generator":
                        state["proposal"] = event
            except (InvalidPolicy, ValueError, TypeError) as exc:
                event["status"] = "invalid_critique" if role == "critic" else "invalid_policy"
                event["error_type"] = type(exc).__name__
        events.append(event)
        _journal(journal, {"phase": "response_processed", **event})
        print(
            f"seed={seed} condition={condition} call={index + 1} role={role} status={event['status']}",
            flush=True,
        )
        if event["status"] in FATAL:
            stop_reason = event["status"]
            break
    return {
        "seed": seed,
        "condition": condition,
        "events": events,
        "tokens_accounted": tokens,
        "usage_complete": usage_complete,
        "stop_reason": stop_reason,
        "complete": stop_reason == "call_limit"
        and len(events) == config["calls_per_condition"]
        and usage_complete,
        "archive": archive.summary(),
        "fallback_reference": best_name,
        "target_setup": {
            "reachable_cells": len(library),
            "distinct_witness_behaviors": sum(map(len, library.values())),
        },
    }


def audit_condition(run, train, validation, test, margin):
    train_references, test_references = reference_scores(train), reference_scores(test)
    candidates = [event for event in run["events"] if event["status"] == "ok" and "policy" in event]
    for event in candidates:
        policy = Policy.from_object(event["policy"])
        score = evaluate(policy, test)
        event["audit"] = {
            "validation": evaluate(policy, validation),
            "test": score,
            "utility_success": successful(score, test_references, margin),
            "novelty": "unresolved"
            if event["verification"]["verdict"] == "unresolved"
            else "known_reference_equivalent",
        }
    eligible = [
        event for event in candidates if successful(event["train"], train_references, margin)
    ]
    winner = max(eligible, key=lambda e: e["train"]["fitness"], default=None)
    best_generated = max(candidates, key=lambda e: e["train"]["fitness"], default=None)
    selected = (
        Policy.from_object(winner["policy"]) if winner else REFERENCES[run["fallback_reference"]]
    )
    selected_test = evaluate(selected, test)
    status = (
        "no_training_improvement"
        if winner is None
        else "utility_screen_passed_novelty_unresolved"
        if winner["audit"]["utility_success"]
        else "training_candidate_failed_holdout_screen"
    )
    if not run["complete"]:
        status = "incomplete_comparison"
    run["summary"] = {
        "calls": len(run["events"]),
        "valid_policies": len(candidates),
        "tokens_accounted": run["tokens_accounted"],
        "request_wall_seconds": sum(
            e["response_metadata"].get("wall_seconds", 0) for e in run["events"]
        ),
        "valid_critiques": sum(
            e["status"] == "ok" and e["role"] == "critic" for e in run["events"]
        ),
        "unique_policies": len({e["candidate_id"] for e in candidates}),
        "utility_successes": sum(e["audit"]["utility_success"] for e in candidates),
        "known_reference_equivalent_attempts": sum(
            e["verification"]["verdict"] == "known_reference_equivalent" for e in candidates
        ),
        "target_attempts": sum(e["target_reached"] is not None for e in candidates),
        "target_hits": sum(e["target_reached"] is True for e in candidates),
        "best_generated_test_bins": best_generated["audit"]["test"]["total_bins"]
        if best_generated
        else None,
        "selected_policy": selected.to_object(),
        "selected_test_bins": selected_test["total_bins"],
        "used_reference_fallback": winner is None,
        "outcome": status,
        "validated_novel_discoveries": None,
    }


def run_study(config, backend, output, root):
    output, root = Path(output), Path(root)
    corpus = load_corpus(root / "data/corpus/frozen-review-notes-v1.json")
    if corpus["corpus_sha256"] != config["corpus_sha256"]:
        raise ValueError("knowledge corpus differs from configured snapshot")
    panel_record = build_panel_record(config, root)
    panel = panel_from_record(panel_record)
    output.mkdir(parents=True, exist_ok=False)
    suites = {
        split: make_suite(split, config["per_family"]) for split in ("train", "validation", "test")
    }
    for split in suites:
        write_json(output / f"{split}.json", suite_record(split, config["per_family"]))
    write_json(output / "probe_panel.json", panel_record)
    write_json(output / "knowledge_corpus.json", corpus)
    manifest = {
        "experiment_kind": "coordinator-v1",
        "status": "running",
        "config": config,
        "config_sha256": digest(config),
        "backend": backend.identity(),
        "source": source_manifest(root),
        "started_utc": datetime.now(UTC).isoformat(),
        "condition_order": [],
        "input_files": {p.name: file_hash(p) for p in output.glob("*.json")},
    }
    write_json(output / "run_manifest.json", manifest)
    snapshot_source(root, manifest["source"], output / "source.zip")
    runs = []
    try:
        with (output / "events.jsonl").open("x", encoding="utf-8") as journal:
            fatal = False
            for seed in config["seeds"]:
                order = list(CONDITIONS)
                random.Random(seed + 909).shuffle(order)
                manifest["condition_order"].append({"seed": seed, "conditions": order})
                write_json(output / "run_manifest.json", manifest)
                for condition in order:
                    if fatal:
                        break
                    run = run_condition(
                        config,
                        backend,
                        seed,
                        condition,
                        suites["train"],
                        panel,
                        output / "knowledge_corpus.json",
                        journal,
                    )
                    runs.append(run)
                    write_json(output / "generation.json", runs)
                    fatal = run["stop_reason"] in FATAL
                if fatal:
                    break
        # Holdout results never enter role prompts; all conditions finish first.
        for run in runs:
            audit_condition(
                run,
                suites["train"],
                suites["validation"],
                suites["test"],
                config["minimum_improvement"],
            )
        write_json(output / "runs.json", runs)
        manifest["status"] = (
            "completed"
            if len(runs) == len(config["seeds"]) * len(CONDITIONS)
            and all(run["complete"] for run in runs)
            else "incomplete_comparison"
        )
    except BaseException as exc:
        manifest.update(
            status="interrupted" if isinstance(exc, KeyboardInterrupt) else "failed",
            error_type=type(exc).__name__,
        )
        raise
    finally:
        manifest["finished_utc"] = datetime.now(UTC).isoformat()
        manifest["output_files"] = {
            p.name: file_hash(p)
            for p in output.iterdir()
            if p.is_file() and p.name != "run_manifest.json"
        }
        write_json(output / "run_manifest.json", manifest)
    return manifest["status"], runs


class RecordedBackend:
    def __init__(self, identity, events):
        self._identity, self.events, self.position = identity, events, 0
        self.context = identity["options"]["num_ctx"]

    def identity(self):
        return self._identity

    def generate(self, system, prompt, output_format, seed):
        event = self.events[self.position]
        self.position += 1
        if event["request"] != {
            "system": system,
            "prompt": prompt,
            "format": output_format,
            "seed": seed,
        }:
            raise ValueError("role request replay mismatch")
        return Proposal(
            event["response_text"],
            event["usage"],
            event["response_metadata"],
            event["provider_status"],
        )


def replay(output):
    output = Path(output)
    verify_artifacts(output)
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("experiment_kind") != "coordinator-v1" or manifest["status"] not in (
        "completed",
        "incomplete_comparison",
    ):
        raise ValueError("not a finalized coordinator run")
    config = manifest["config"]
    panel = saved_panel(output, config)
    suites = {}
    for split in ("train", "validation", "test"):
        data = json.loads((output / f"{split}.json").read_text(encoding="utf-8"))
        if digest(data["instances"]) != data["sha256"]:
            raise ValueError("suite hash mismatch")
        suites[split] = tuple(
            Instance(**{**row, "items": tuple(row["items"])}) for row in data["instances"]
        )
    expected = json.loads((output / "runs.json").read_text(encoding="utf-8"))
    journal = [
        json.loads(line)
        for line in (output / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    starts = [entry for entry in journal if entry["phase"] == "request_started"]
    responses = [entry for entry in journal if entry["phase"] == "response_processed"]
    recorded_events = [event for run in expected for event in run["events"]]
    if len(starts) != len(responses) or len(responses) != len(recorded_events):
        raise ValueError("unresolved or missing journal requests")
    for start, response, event in zip(starts, responses, recorded_events):
        if start["event_id"] != event["event_id"] or start["request"] != event["request"]:
            raise ValueError("request journal mismatch")
        if {k: v for k, v in response.items() if k != "phase"} != {
            k: v for k, v in event.items() if k != "audit"
        }:
            raise ValueError("response journal mismatch")
    calls = 0
    for original in expected:
        backend = RecordedBackend(manifest["backend"], original["events"])
        actual = run_condition(
            config,
            backend,
            original["seed"],
            original["condition"],
            suites["train"],
            panel,
            output / "knowledge_corpus.json",
            io.StringIO(),
        )
        audit_condition(
            actual,
            suites["train"],
            suites["validation"],
            suites["test"],
            config["minimum_improvement"],
        )
        if actual != original or backend.position != len(original["events"]):
            raise ValueError("coordinator state replay mismatch")
        calls += backend.position
    return {"replay": "matched", "role_calls_recomputed": calls, "model_calls": 0}


def report(output):
    output = Path(output)
    verify_artifacts(output)
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    runs = json.loads((output / "runs.json").read_text(encoding="utf-8"))
    lines = [
        "# Coordinator engineering pilot",
        "",
        f"Status: **{manifest['status']}**. Model: `{manifest['backend']['model']}`.",
        "",
        "All conditions share call/token ceilings. Critique consumes those allowances; candidate counts differ intentionally. This is an end-to-end feasibility comparison, not a powered efficacy test.",
        "",
        "| Seed | Condition | Calls | Valid policies | Valid critiques | Target hits / attempts | Best generated test bins | Fallback | Selected test bins | Outcome |",
        "|---:|---|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for run in runs:
        s = run["summary"]
        lines.append(
            f"| {run['seed']} | {run['condition']} | {s['calls']} | {s['valid_policies']} | {s['valid_critiques']} | {s['target_hits']}/{s['target_attempts']} | {s['best_generated_test_bins']} | {s['used_reference_fallback']} | {s['selected_test_bins']} | {s['outcome']} |"
        )
    lines.extend(
        [
            "",
            "| Seed | Condition | Accounted tokens | Request seconds | Utility successes |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for run in runs:
        s = run["summary"]
        lines.append(
            f"| {run['seed']} | {run['condition']} | {s['tokens_accounted']} | {s['request_wall_seconds']:.1f} | {s['utility_successes']} |"
        )
    lines.extend(
        [
            "",
            "The target witness library uses generated probe behaviors, not a comprehensive knowledge corpus. Source retrieval uses four reviewed notes with unmeasured recall. Known-reference equivalence can reject some rediscoveries; all other novelty remains unresolved. These roles share a local model and are not independent expert judgments.",
            "",
            "All generation precedes holdout scoring. Fallback selection uses training data only; best-generated scores are the test results of each condition's training-best generated candidate, reported separately so fallback cannot hide poor generation. The reused pilot holdout is exploratory, not fresh confirmation. No global novelty or statistical superiority is asserted.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    for name in ("replay", "report"):
        command = sub.add_parser(name)
        command.add_argument("run", type=Path)
        if name == "report":
            command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run":
        config = load_config(args.config)
        backend = LocalBackend(config["model"], config["max_output_tokens"], structured=True)
        status, _ = run_study(config, backend, args.output, Path.cwd())
        print(status)
        if status != "completed":
            raise SystemExit(2)
    elif args.command == "replay":
        print(json.dumps(replay(args.run), indent=2))
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report(args.run), encoding="utf-8")


if __name__ == "__main__":
    main()
