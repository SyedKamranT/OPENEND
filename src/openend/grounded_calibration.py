"""Prospectively fixed critic and controllability gates with zero-call replay."""

import argparse
import json
from pathlib import Path

from . import evidence
from .artifacts import canonical, file_hash, snapshot_source, source_manifest, write_json
from .benchmark import Instance, make_suite, suite_record
from .experiment import verify_artifacts
from .local import LocalBackend
from .policy import Policy
from .research_diagnostics import assess_target, target_requests
from .role_calibration import CASES

CONFIG = {
    "version": "grounded-calibration-v2",
    "model": "qwen3.5:4b",
    "calls": 9,
    "tokens": 40000,
    "max_output_tokens": 384,
}


def requests():
    for i, case in enumerate(CASES):
        policy = Policy.from_object({"expression": case["expression"]})
        yield {
            "kind": "critic",
            "case_id": case["id"],
            "arm": "grounded",
            "seed": 16001 + i,
            "system": evidence.SYSTEM,
            "payload": {"policy": policy.to_object(), "traces": evidence.behavior_evidence(policy)},
            "schema": evidence.schema(),
        }
    yield from target_requests()


def assess(text, request, train):
    if request["kind"] == "target":
        return assess_target(text, request)
    return evidence.assess(text, Policy.from_object(request["payload"]["policy"]), train)


def summarize(events):
    accounted = [e["usage"].get("total_tokens") for e in events]
    usage_complete = all(type(x) is int and x >= 0 for x in accounted)
    tokens = sum(x for x in accounted if type(x) is int and x >= 0)
    complete = (
        len(events) == CONFIG["calls"]
        and usage_complete
        and tokens <= CONFIG["tokens"]
        and all(e["status"] == "ok" for e in events)
    )
    groups = {}
    for arm, metric in (
        ("grounded", "accepted"),
        ("target_only", "target_hit"),
        ("witness_control", "target_hit"),
    ):
        rows = [e for e in events if e["request"]["arm"] == arm]
        successes = sum(e["assessment"].get(metric, False) for e in rows)
        groups[arm] = {
            "calls": len(rows),
            "successes": successes,
            "gate_passed": complete and successes == 3,
        }
    return {
        "complete": complete,
        "groups": groups,
        "tokens": tokens,
        "usage_complete": usage_complete,
    }


def run(output, backend, root):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    train = make_suite("train", 12)
    source = source_manifest(root)
    snapshot_source(root, source, output / "source.zip")
    write_json(output / "train.json", suite_record("train", 12))
    write_json(output / "requests.json", list(requests()))
    (output / "protocol.md").write_text(
        (Path(root) / "docs/grounded-calibration-v2-protocol.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    identity = backend.identity()
    manifest = {
        "experiment_kind": CONFIG["version"],
        "status": "running",
        "config": CONFIG,
        "backend": identity,
        "source": source,
        "input_files": {p.name: file_hash(p) for p in output.iterdir()},
    }
    write_json(output / "run_manifest.json", manifest)
    events, spent = [], 0
    write_json(output / "events.json", events)
    try:
        with (output / "events.jsonl").open("x", encoding="utf-8") as journal:
            for request in requests():
                prompt = canonical(request["payload"])
                reserve = (
                    len((request["system"] + prompt).encode()) + 512 + CONFIG["max_output_tokens"]
                )
                if reserve > backend.context or spent + reserve > CONFIG["tokens"]:
                    break
                journal.write(canonical({"phase": "started", "request": request}) + "\n")
                journal.flush()
                response = backend.generate(
                    request["system"], prompt, request["schema"], request["seed"]
                )
                usage = response.usage.get("total_tokens")
                status = response.status
                if type(usage) is not int or usage < 0:
                    status = "missing_usage"
                else:
                    spent += usage
                if (
                    response.metadata.get("model")
                    != identity["model"] + "@" + identity["model_digest"]
                ):
                    status = "model_changed"
                if spent > CONFIG["tokens"]:
                    status = "budget_overrun"
                event = {
                    "request": request,
                    "response": response.text,
                    "usage": response.usage,
                    "metadata": response.metadata,
                    "status": status,
                    "assessment": assess(response.text, request, train)
                    if status == "ok"
                    else {"valid": False},
                }
                events.append(event)
                journal.write(canonical({"phase": "processed", **event}) + "\n")
                journal.flush()
                write_json(output / "events.json", events)
                print(request["case_id"], request["arm"], status, flush=True)
                if status in ("api_error", "missing_usage", "model_changed", "budget_overrun"):
                    break
        summary = summarize(events)
        write_json(output / "summary.json", summary)
        manifest["status"] = "completed" if summary["complete"] else "incomplete"
    except BaseException:
        manifest["status"] = "interrupted_or_failed"
        raise
    finally:
        manifest["output_files"] = {
            p.name: file_hash(p) for p in output.iterdir() if p.name != "run_manifest.json"
        }
        write_json(output / "run_manifest.json", manifest)
    return summary


def replay(output):
    output = Path(output)
    verify_artifacts(output)
    manifest = json.loads((output / "run_manifest.json").read_text())
    if manifest["config"] != CONFIG or manifest["status"] not in ("completed", "incomplete"):
        raise ValueError("not a finalized calibration")
    expected = list(requests())
    if json.loads((output / "requests.json").read_text()) != expected:
        raise ValueError("request plan mismatch")
    data = json.loads((output / "train.json").read_text())
    if canonical(data) != canonical(suite_record("train", 12)):
        raise ValueError("training suite mismatch")
    train = tuple(Instance(**{**row, "items": tuple(row["items"])}) for row in data["instances"])
    events = json.loads((output / "events.json").read_text())
    journal = [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines()]
    if len(events) > len(expected) or len(journal) != 2 * len(events):
        raise ValueError("unresolved journal or extra calls")
    for i, event in enumerate(events):
        request = expected[i]
        if (
            event["request"] != request
            or journal[2 * i] != {"phase": "started", "request": request}
            or journal[2 * i + 1] != {"phase": "processed", **event}
        ):
            raise ValueError("request/journal mismatch")
        actual = (
            assess(event["response"], request, train)
            if event["status"] == "ok"
            else {"valid": False}
        )
        if actual != event["assessment"]:
            raise ValueError("claim/target assessment mismatch")
    if summarize(events) != json.loads((output / "summary.json").read_text()):
        raise ValueError("summary mismatch")
    return {"replay": "matched", "calls": len(events), "model_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "replay"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "replay":
        result = replay(args.output)
    else:
        backend = LocalBackend(CONFIG["model"], CONFIG["max_output_tokens"], structured=True)
        try:
            result = run(args.output, backend, Path.cwd())
        finally:
            backend._request("generate", {"model": CONFIG["model"], "keep_alive": 0})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
