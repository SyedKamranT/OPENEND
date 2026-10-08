"""Paired pilot runs with generation completed before held-out scoring."""

import json
import platform
import random
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

from .artifacts import digest, file_hash, snapshot_source, source_manifest, write_json
from .backends import SYSTEM_PROMPT, prompt_for
from .benchmark import evaluate, make_suite, reference_scores, successful, suite_record
from .policy import REFERENCES, InvalidPolicy, Policy
from .search import Archive, corpus_manifest, novelty_screen, signature, sparsity


def load_config(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "version",
        "purpose",
        "seeds",
        "candidates_per_arm",
        "total_tokens_per_arm",
        "max_output_tokens",
        "per_family",
        "grid_resolution",
        "minimum_improvement",
        "reasoning_effort",
    }
    if not isinstance(value, dict) or set(value) != required or value["purpose"] != "pilot":
        raise ValueError("expected a pilot configuration with the documented fields")
    for key, low, high in [
        ("candidates_per_arm", 1, 1000),
        ("total_tokens_per_arm", 1, 1000000),
        ("max_output_tokens", 16, 8192),
        ("per_family", 1, 100),
        ("grid_resolution", 2, 20),
    ]:
        if type(value[key]) is not int or not low <= value[key] <= high:
            raise ValueError(f"invalid configuration field: {key}")
    seeds = value["seeds"]
    if (
        not isinstance(seeds, list)
        or not 1 <= len(seeds) <= 100
        or any(type(x) is not int or not 0 <= x < 2**32 for x in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise ValueError("seeds must be unique nonnegative integers")
    if (
        type(value["minimum_improvement"]) not in (int, float)
        or not 0 < value["minimum_improvement"] < 1
    ):
        raise ValueError("invalid improvement margin")
    if value["reasoning_effort"] not in ("none", "low", "medium", "high"):
        raise ValueError("invalid reasoning effort")
    return value


def _search(config, seed, arm, backend, train, event_file):
    archive = Archive(config["grid_resolution"])
    for policy in REFERENCES.values():
        archive.insert(policy, evaluate(policy, train)["fitness"])
    selection_rng, mutation_rng = random.Random(seed + 111), random.Random(seed + 222)
    events, tokens, stop_reason = [], 0, "candidate_limit"
    known_usage = True
    observed_model = None
    for attempt in range(config["candidates_per_arm"]):
        parent, fitness, _ = archive.select(selection_rng, sparse=arm == "sparse_on")
        prompt = prompt_for(parent, fitness)
        reservation = backend.reservation(prompt)
        if tokens + reservation > config["total_tokens_per_arm"]:
            stop_reason = "token_reservation_limit"
            break
        result = backend.propose(parent, fitness, mutation_rng)
        usage = result.usage.get("total_tokens")
        if type(usage) is not int or usage < 0:
            known_usage = False
            tokens += reservation
        else:
            tokens += usage
        event = {
            "event_id": f"{seed}/{arm}/{attempt:04}",
            "seed": seed,
            "arm": arm,
            "attempt": attempt,
            "parent_id": parent.identity,
            "prompt": prompt,
            "response_text": result.text,
            "response_metadata": result.metadata,
            "usage": result.usage,
            "tokens_accounted_so_far": tokens,
            "reservation": reservation,
            "status": result.status,
        }
        if result.status == "ok":
            actual_model = result.metadata.get("model")
            if observed_model is not None and actual_model != observed_model:
                event["status"] = "model_changed"
            observed_model = actual_model
            try:
                policy = Policy.from_text(result.text)
                score = evaluate(policy, train)
                event.update(
                    {
                        "candidate_id": policy.identity,
                        "policy": policy.to_object(),
                        "train": score,
                        "sparsity_proxy": sparsity(signature(policy)),
                    }
                )
                if event["status"] == "ok":
                    archive.insert(policy, score["fitness"])
            except InvalidPolicy as exc:
                event["status"] = "invalid_policy"
                event["error"] = str(exc)
        if tokens > config["total_tokens_per_arm"]:
            event["status"] = "budget_overrun"
        events.append(event)
        event_file.write(json.dumps(event, allow_nan=False) + "\n")
        event_file.flush()
        if event["status"] in ("api_error", "missing_usage", "budget_overrun", "model_changed"):
            stop_reason = event["status"]
            break
    return {
        "seed": seed,
        "arm": arm,
        "events": events,
        "archive": archive.summary(),
        "stop_reason": stop_reason,
        "tokens_accounted": tokens,
        "usage_complete": known_usage,
        "observed_model": observed_model,
        "initial_reference_evaluations": len(REFERENCES),
    }


def _audit(run, validation, test, references, improvement):
    successes, known, unresolved, unique_valid = 0, 0, 0, set()
    unresolved_successes, seen_probe = set(), set()
    finalists = [e for e in run["events"] if e["status"] == "ok"]
    winner = max(finalists, key=lambda e: (e["train"]["fitness"], -e["attempt"]), default=None)
    for event in run["events"]:
        if event["status"] != "ok":
            continue
        policy = Policy.from_object(event["policy"])
        screen = novelty_screen(policy)
        val_result, test_result = evaluate(policy, validation), evaluate(policy, test)
        is_success = successful(test_result, references, improvement)
        event["audit"] = {
            "validation": val_result,
            "test": test_result,
            "novelty": screen,
            "utility_success": is_success,
        }
        successes += is_success
        known += screen["verdict"] == "known_reference"
        unresolved += screen["verdict"] == "unresolved"
        if is_success and screen["verdict"] == "unresolved":
            unresolved_successes.add(policy.identity)
        unique_valid.add(policy.identity)
        seen_probe.add(screen["probe_sha256"])
    n = len(run["events"])
    valid = len(finalists)
    unknown_success_attempts = sum(
        e.get("audit", {}).get("utility_success", False)
        and e["audit"]["novelty"]["verdict"] == "unresolved"
        for e in finalists
    )
    run["summary"] = {
        "attempts": n,
        "valid_candidates": valid,
        "unique_syntax_candidates": len(unique_valid),
        "unique_probe_signatures": len(seen_probe),
        "duplicate_syntax_rate": 1 - len(unique_valid) / valid if valid else None,
        "utility_successes": successes,
        "utility_success_rate": successes / n if n else None,
        "known_reference_attempts": known,
        "novelty_unresolved_attempts": unresolved,
        "validated_novel_success_rate": None,
        "nsr_bounds": [0, unknown_success_attempts / n] if n else None,
        "unique_unresolved_successful_policies": len(unresolved_successes),
        "selected_candidate_id": winner["candidate_id"] if winner else None,
        "selected_test_bins": winner["audit"]["test"]["total_bins"] if winner else None,
        "selected_test_fitness": winner["audit"]["test"]["fitness"] if winner else None,
        **run["archive"],
    }


def paired_analysis(runs):
    rows = []
    for seed in sorted({r["seed"] for r in runs}):
        pair = {r["arm"]: r for r in runs if r["seed"] == seed}
        a, b = pair["sparse_off"], pair["sparse_on"]
        eligible = (
            a["stop_reason"] == b["stop_reason"] == "candidate_limit"
            and a["usage_complete"]
            and b["usage_complete"]
            and a["observed_model"] == b["observed_model"]
        )
        delta = {}
        for key in (
            "utility_success_rate",
            "coverage",
            "selected_test_bins",
            "selected_test_fitness",
        ):
            left, right = a["summary"][key], b["summary"][key]
            delta[key] = right - left if left is not None and right is not None else None
        rows.append({"seed": seed, "eligible_complete_pair": eligible, "on_minus_off": delta})
    aggregate = {}
    for key in ("utility_success_rate", "coverage", "selected_test_bins", "selected_test_fitness"):
        values = [
            r["on_minus_off"][key]
            for r in rows
            if r["eligible_complete_pair"] and r["on_minus_off"][key] is not None
        ]
        aggregate[key] = mean(values) if values else None
    return {
        "status": "descriptive_pilot_only",
        "pairs": rows,
        "mean_paired_differences": aggregate,
        "p_value": None,
        "novelty_hypothesis": "not_testable_without_independent_novelty_labels",
        "scope": "Repeated search seeds on one fixed benchmark; not independent task families.",
    }


def run_study(config, backend, output, root):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)  # Never overwrite a previous experiment.
    splits = {
        name: make_suite(name, config["per_family"]) for name in ("train", "validation", "test")
    }
    manifest = {
        "schema_version": 1,
        "status": "running",
        "purpose": "pilot",
        "started_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "config_sha256": digest(config),
        "backend": backend.identity(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "source": source_manifest(root),
        "prompt_sha256": digest(SYSTEM_PROMPT),
        "arm_order": [],
        "final_novelty_verifier": "exact_reference_screen_only_unresolved_otherwise",
    }
    for name in splits:
        write_json(output / f"{name}.json", suite_record(name, config["per_family"]))
    write_json(output / "corpus_manifest.json", corpus_manifest())
    manifest["input_files"] = {p.name: file_hash(p) for p in sorted(output.glob("*.json"))}
    write_json(output / "run_manifest.json", manifest)
    snapshot_source(root, manifest["source"], output / "source.zip")
    runs = []
    try:
        with (output / "events.jsonl").open("x", encoding="utf-8") as events:
            for seed in config["seeds"]:
                order = ["sparse_off", "sparse_on"]
                random.Random(seed + 333).shuffle(order)
                manifest["arm_order"].append({"seed": seed, "order": order})
                write_json(output / "run_manifest.json", manifest)
                for arm in order:
                    print(f"Running seed={seed} arm={arm} backend={backend.kind}", flush=True)
                    runs.append(_search(config, seed, arm, backend, splits["train"], events))
        # All generation ends before either held-out split is scored.
        references = {name: reference_scores(suite) for name, suite in splits.items()}
        write_json(output / "reference_scores.json", references)
        for run in runs:
            _audit(
                run,
                splits["validation"],
                splits["test"],
                references["test"],
                config["minimum_improvement"],
            )
        write_json(output / "runs.json", runs)
        analysis = paired_analysis(runs)
        write_json(output / "analysis.json", analysis)
        manifest["status"] = (
            "completed"
            if all(r["eligible_complete_pair"] for r in analysis["pairs"])
            else "incomplete_comparison"
        )
    except BaseException as exc:
        manifest["status"] = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
        manifest["error_type"] = type(exc).__name__
        raise
    finally:
        manifest["finished_utc"] = datetime.now(UTC).isoformat()
        manifest["output_files"] = {
            p.name: file_hash(p)
            for p in sorted(output.iterdir())
            if p.is_file() and p.name != "run_manifest.json"
        }
        write_json(output / "run_manifest.json", manifest)
    return manifest["status"], analysis


def verify_artifacts(output):
    output = Path(output)
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    checked = 0
    for group in ("input_files", "output_files"):
        for name, expected in manifest[group].items():
            if Path(name).name != name or file_hash(output / name) != expected:
                raise ValueError(f"artifact hash mismatch: {name}")
            checked += 1
    return {"status": manifest["status"], "hashes_verified": checked}


def replay_study(output):
    """Recompute scores and summaries from recorded inputs, without any API request."""
    from .benchmark import Instance

    output = Path(output)
    verify_artifacts(output)
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    runs = json.loads((output / "runs.json").read_text(encoding="utf-8"))
    suites = {}
    for split in ("train", "validation", "test"):
        data = json.loads((output / f"{split}.json").read_text(encoding="utf-8"))
        if digest(data["instances"]) != data["sha256"]:
            raise ValueError("invalid suite content hash")
        suites[split] = tuple(
            Instance(**{**row, "items": tuple(row["items"])}) for row in data["instances"]
        )
    ref = reference_scores(suites["test"])
    candidates = 0
    for run in runs:
        old_summary = run["summary"]
        old_audits = [e.get("audit") for e in run["events"]]
        for event in run["events"]:
            if event["status"] == "ok":
                actual = evaluate(Policy.from_object(event["policy"]), suites["train"])
                if actual != event["train"]:
                    raise ValueError("training replay mismatch")
                candidates += 1
        _audit(
            run,
            suites["validation"],
            suites["test"],
            ref,
            manifest["config"]["minimum_improvement"],
        )
        if run["summary"] != old_summary or old_audits != [e.get("audit") for e in run["events"]]:
            raise ValueError("final evaluation replay mismatch")
    expected = json.loads((output / "analysis.json").read_text(encoding="utf-8"))
    if paired_analysis(runs) != expected:
        raise ValueError("paired analysis replay mismatch")
    return {"replay": "matched", "candidates_recomputed": candidates, "api_calls": 0}
