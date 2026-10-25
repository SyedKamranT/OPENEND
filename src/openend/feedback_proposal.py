"""Frozen, bounded local-model comparison of regression-aware proposal feedback."""

import argparse
import json
import random
from pathlib import Path

from .artifacts import canonical, digest, file_hash, snapshot_source, source_manifest, write_json
from .benchmark import evaluate, make_suite, pack, reference_scores, successful
from .benchmark_diagnostics import SEEDS, policies, stress_panel
from .coordinated_sketch import trace_effect
from .decision_diagnostic import completion
from .grammar import policy_schema
from .local import LocalBackend
from .operator_comparison import trajectory
from .policy import Policy
from .search import PROBES, signature, sparsity
from .utility_runner import SYSTEM, parse

ARMS = ("none", "beneficial", "mixed")
MODEL_DIGEST = "d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04"
INTERVENTION = ["neg", ["abs", ["sub", "gap", ["mul", 1, "item"]]]]
CONFIG = {
    "model": "qwen3.5:4b",
    "model_digest": MODEL_DIGEST,
    "seeds": [2026102601, 2026102602],
    "output_tokens": 256,
    "context": 8192,
    "tokens_per_arm": 40000,
    "calls_per_arm": 4,
}


def size(tree):
    return 1 + sum(size(x) for x in tree[1:]) if isinstance(tree, list) else 1


def bounded_revision(parent, child):
    """A changed subtree may be below, but never at, the original root."""
    a, b = parent.to_object()["expression"], child.to_object()["expression"]
    if a == b:
        return True

    def one_subtree(x, y):
        if size(y) <= 7:
            return True
        if not isinstance(x, list) or not isinstance(y, list) or x[0] != y[0]:
            return False
        changes = [(u, v) for u, v in zip(x[1:], y[1:]) if u != v]
        return len(x) == len(y) and len(changes) == 1 and one_subtree(*changes[0])

    if not isinstance(a, list) or not isinstance(b, list) or a[0] != b[0] or len(a) != len(b):
        return False
    changes = [(x, y) for x, y in zip(a[1:], b[1:]) if x != y]
    return len(changes) == 1 and one_subtree(*changes[0])


def examples(traces):
    policy = Policy.from_object({"expression": INTERVENTION})
    suite = {x.instance_id: x for x in make_suite("train", 12)}
    groups = {"beneficial": [], "harmful": []}
    used = {k: set() for k in groups}
    for row in sorted(traces, key=lambda r: r["instance_id"]):
        for state in row["states"]:
            action = policy.choose(state["item"], state["remaining"], 100)
            bins = next(x["bins"] for x in state["action_bins"] if x["action"] == action)
            gain = state["default_completion_bins"] - bins
            if gain == 0:
                continue
            kind = "beneficial" if gain > 0 else "harmful"
            if len(groups[kind]) == 2 or row["instance_id"] in used[kind]:
                continue
            actual, _ = completion(
                suite[row["instance_id"]],
                row["assignments"][: state["step"]],
                state["remaining"],
                action,
            )
            assert actual == bins
            groups[kind].append(
                {
                    "item": state["item"],
                    "remaining": state["remaining"],
                    "bf_action": state["default_action"],
                    "alternative_action": action,
                    "bf_completion_bins": state["default_completion_bins"],
                    "alternative_completion_bins": bins,
                }
            )
            used[kind].add(row["instance_id"])
    assert all(len(v) == 2 for v in groups.values())
    return groups


def requests(traces):
    evidence = examples(traces)
    suite = make_suite("train", 12)
    rows = []
    for index, name in enumerate(("best_fit", "historical_witness")):
        parent = policies()[name]
        score = evaluate(parent, suite)
        for seed in CONFIG["seeds"]:
            arms = list(ARMS)
            random.Random(seed + index).shuffle(arms)
            for arm in arms:
                feedback = [] if arm == "none" else evidence["beneficial"]
                if arm == "mixed":
                    feedback = feedback + evidence["harmful"]
                prompt = canonical(
                    {
                        "parent": parent.to_object(),
                        "total_training_bins": score["total_bins"],
                        "task": "Reduce full-trajectory total bins. Replace at most one non-root subtree "
                        "with at most seven nodes. Preserve everything else. Keep the root operator. "
                        "Selection falls back to the parent unless total improves and family limits pass.",
                        "example_intervention": {"expression": INTERVENTION},
                        "label_scope": "Examples force one action after a BF prefix, then finish with BF. "
                        "They are not labels for states reached by your revised policy. Avoid broad "
                        "regressions; fit the existing grammar. No future information at runtime.",
                        "examples": feedback,
                    }
                )
                assert len((SYSTEM + prompt).encode()) + 512 + 256 <= 8192
                rows.append(
                    {
                        "arm": arm,
                        "parent": name,
                        "seed": seed,
                        "request": {
                            "system": SYSTEM,
                            "prompt": prompt,
                            "schema": policy_schema(),
                            "seed": seed,
                        },
                    }
                )
    return rows


def score_response(row, response, traces):
    result = {"status": response["status"], "selected_bins": None}
    parent = policies()[row["parent"]]
    suite = make_suite("train", 12)
    parent_score = evaluate(parent, suite)
    result["selected_bins"] = parent_score["total_bins"]
    if response["status"] != "ok":
        return result
    try:
        child = parse(response["text"])
    except ValueError:
        result["status"] = "invalid"
        return result
    if not bounded_revision(parent, child):
        result["status"] = "out_of_revision_bounds"
        return result
    score = evaluate(child, suite)
    accepted = score["total_bins"] < parent_score["total_bins"] and all(
        score["family_bins"][f] <= 1.05 * n for f, n in parent_score["family_bins"].items()
    )
    refs = reference_scores(suite)
    panels = {"legacy": PROBES, **{str(s): stress_panel(s) for s in SEEDS}}
    result.update(
        score=score,
        accepted=accepted,
        exact_copy=child.identity == parent.identity,
        policy=child.to_object(),
        screen_passed=successful(score, refs),
        beats_incumbent=score["total_bins"] < 1475,
        regresses_parent=score["total_bins"] > parent_score["total_bins"],
        reference_training_agreement=[
            k for k in refs if trajectory(evaluate(policies()[k], suite)) == trajectory(score)
        ],
        trace_effect=trace_effect(child, traces),
        distances={k: sparsity(signature(child, panel), panel) for k, panel in panels.items()},
        certificates=[
            {"instance_id": i.instance_id, "assignments": pack(child, i)[1]} for i in suite
        ],
    )
    if accepted:
        result["selected_bins"] = score["total_bins"]
    return result


def prepare(output):
    output.mkdir(parents=True, exist_ok=False)
    input_path = Path("results/raw/phase4-decision-v1/report.json")
    raw = json.loads(input_path.read_text())
    assert (
        file_hash(input_path)
        == json.loads(input_path.with_name("manifest.json").read_text())["files"]["report.json"]
    )
    source = source_manifest(Path.cwd())
    snapshot_source(Path.cwd(), source, output / "source.zip")
    (output / "protocol.md").write_bytes(Path("docs/feedback-proposal-v1-protocol.md").read_bytes())
    write_json(output / "requests.json", requests(raw["best_fit_traces"]))
    write_json(output / "config.json", CONFIG)
    write_json(
        output / "manifest.json",
        {
            "source": source,
            "input_sha256": file_hash(input_path),
            "files": {
                n: file_hash(output / n)
                for n in ("source.zip", "protocol.md", "requests.json", "config.json")
            },
        },
    )


def load(output):
    manifest = json.loads((output / "manifest.json").read_text())
    assert all(file_hash(output / p) == h for p, h in manifest["files"].items())
    assert all(file_hash(Path(p)) == h for p, h in manifest["source"]["files"].items())
    path = Path("results/raw/phase4-decision-v1/report.json")
    assert file_hash(path) == manifest["input_sha256"]
    traces = json.loads(path.read_text())["best_fit_traces"]
    rows = json.loads((output / "requests.json").read_text())
    assert rows == requests(traces)
    assert json.loads((output / "config.json").read_text()) == CONFIG
    return rows, traces


def run(output):
    rows, _traces = load(output)
    with (output / "events.jsonl").open("x", encoding="utf-8") as stream:
        backend = LocalBackend(CONFIG["model"], 256, structured=True)
        assert backend.identity()["model_digest"] == MODEL_DIGEST
        write_json(output / "backend.json", backend.identity())
        used = dict.fromkeys(ARMS, 0)
        for index, row in enumerate(rows):
            reserve = (
                len((row["request"]["system"] + row["request"]["prompt"]).encode()) + 512 + 256
            )
            if used[row["arm"]] + reserve > CONFIG["tokens_per_arm"]:
                raise ValueError("token reservation exhausted; no call issued")
            stream.write(
                canonical({"event": "started", "index": index, "request_sha256": digest(row)})
                + "\n"
            )
            stream.flush()
            request = row["request"]
            proposal = backend.generate(
                request["system"], request["prompt"], request["schema"], request["seed"]
            )
            response = {
                "text": proposal.text,
                "usage": proposal.usage,
                "metadata": proposal.metadata,
                "status": proposal.status,
            }
            stream.write(
                canonical({"event": "response", "index": index, "response": response}) + "\n"
            )
            stream.flush()
            usage = response["usage"]
            if not all(
                type(usage.get(k)) is int and usage[k] >= 0
                for k in ("input_tokens", "output_tokens", "total_tokens")
            ):
                raise ValueError("missing usage; stopped")
            if usage["total_tokens"] != usage["input_tokens"] + usage["output_tokens"]:
                raise ValueError("inconsistent usage")
            used[row["arm"]] += usage["total_tokens"]
            if (
                response["status"] in ("api_error", "model_changed", "missing_usage")
                or used[row["arm"]] > 40000
            ):
                raise ValueError("fatal response or budget overrun")
            print(
                {"completed": index + 1, "arm": row["arm"], "status": response["status"]},
                flush=True,
            )
    analyze(output)


def analyze(output):
    rows, traces = load(output)
    events = [json.loads(x) for x in (output / "events.jsonl").read_text().splitlines()]
    results = []
    for index, row in enumerate(rows):
        start, response = events[2 * index : 2 * index + 2]
        assert start == {"event": "started", "index": index, "request_sha256": digest(row)}
        assert response["event"] == "response" and response["index"] == index
        results.append(
            {
                "arm": row["arm"],
                "parent": row["parent"],
                "seed": row["seed"],
                "usage": response["response"]["usage"],
                **score_response(row, response["response"], traces),
            }
        )
    assert len(events) == 2 * len(rows)
    report = {"scope": "training-only 12-call feedback pilot", "results": results}
    path = output / "report.json"
    if path.exists():
        assert digest(json.loads(path.read_text())) == digest(report)
        print("Exact response/score replay matched")
    else:
        write_json(path, report)
        write_json(
            output / "output-hashes.json",
            {n: file_hash(output / n) for n in ("backend.json", "events.jsonl", "report.json")},
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "replay"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    {"prepare": prepare, "run": run, "replay": analyze}[args.command](args.output)


if __name__ == "__main__":
    main()
