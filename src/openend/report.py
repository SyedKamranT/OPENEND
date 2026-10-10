"""Generate a descriptive Markdown report from verified experiment artifacts."""

import json
from collections import Counter
from pathlib import Path

from .experiment import verify_artifacts
from .policy import REFERENCES, Policy
from .search import signature


def render_report(run_path):
    path = Path(run_path)
    verify_artifacts(path)
    manifest = json.loads((path / "run_manifest.json").read_text(encoding="utf-8"))
    runs = json.loads((path / "runs.json").read_text(encoding="utf-8"))
    analysis = json.loads((path / "analysis.json").read_text(encoding="utf-8"))
    events = [event for run in runs for event in run["events"]]
    status_counts = dict(sorted(Counter(e["status"] for e in events).items()))
    usage = sum(e["usage"].get("total_tokens", 0) for e in events)
    wall_seconds = sum(e["response_metadata"].get("wall_seconds", 0) for e in events)
    generated = sum(e["usage"].get("output_tokens", 0) for e in events)
    generation_seconds = (
        sum(e["response_metadata"].get("eval_duration", 0) or 0 for e in events) / 1e9
    )
    parent_signatures = {policy.identity: signature(policy) for policy in REFERENCES.values()}
    for event in events:
        if "policy" in event:
            policy = Policy.from_object(event["policy"])
            parent_signatures[policy.identity] = signature(policy)
    paired_parents = different_parents = different_parent_behaviors = 0
    for seed in {run["seed"] for run in runs}:
        arms = {run["arm"]: run for run in runs if run["seed"] == seed}
        for left, right in zip(arms["sparse_off"]["events"], arms["sparse_on"]["events"]):
            paired_parents += 1
            different_parents += left["parent_id"] != right["parent_id"]
            different_parent_behaviors += (
                parent_signatures[left["parent_id"]] != parent_signatures[right["parent_id"]]
            )
    contrasts = [
        e["selection"]["total_variation_from_uniform"]
        for run in runs
        if run["arm"] == "sparse_on"
        for e in run["events"]
        if "selection" in e
    ]
    mean_contrast = sum(contrasts) / len(contrasts) if contrasts else None
    output = [
        "# Bin-packing pilot results",
        "",
        f"Run: `{path.as_posix()}`. Status: **{manifest['status']}**.",
        f"Backend: `{manifest['backend']['kind']}`; model: `{manifest['backend']['model']}`.",
        "",
        f"Recorded attempt events: **{len(events)}**. Status counts: `{status_counts}`.",
        f"Provider-reported total tokens: **{usage}** (unknown usage is not imputed as free).",
        "Setup reference evaluations are separate from generated attempts.",
        f"Recorded request wall time: {wall_seconds:.1f} seconds (when supplied by the backend).",
        f"Generated tokens: {generated}; recorded generation time: {generation_seconds:.1f} seconds.",
        f"Different selected parents at paired attempt positions: **{different_parents}/{paired_parents}**.",
        "If no paired parents differ, this run does not exercise different parent choices.",
        f"Different parent probe behaviors at paired positions: **{different_parent_behaviors}/{paired_parents}**.",
        f"Mean sparse-arm selection total variation from uniform: `{mean_contrast}`.",
        "",
        (
            "Both arms use identical configured allowances, initial references, QD grid, probes, "
            "and evaluator. Parent-selection weights are the treatment. Seeds replicate search "
            "on one fixed benchmark; they do not replicate independent task families."
        ),
        "",
        "| Seed | Arm | Valid / attempts | Unique syntax / probes | Coverage | Selected test bins | Utility successes | Stop |",
        "|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for run in sorted(runs, key=lambda r: (r["seed"], r["arm"])):
        s = run["summary"]
        output.append(
            f"| {run['seed']} | {run['arm']} | {s['valid_candidates']} / {s['attempts']} | "
            f"{s['unique_syntax_candidates']} / {s['unique_probe_signatures']} | "
            f"{s['coverage']:.4f} | {s['selected_test_bins']} | {s['utility_successes']} | "
            f"{run['stop_reason']} |"
        )
    output.extend(
        [
            "",
            (
                "Selection uses training fitness only. All generation ends before held-out scoring. "
                "Utility success is the predeclared 1% aggregate improvement / 5% family-regression screen."
            ),
            "",
            "## Paired differences (sparse on minus off)",
            "",
        ]
    )
    for key, value in analysis["mean_paired_differences"].items():
        output.append(f"- `{key}`: `{value}`")
    output.extend(
        [
            "",
            (
                "Only complete, usage-accounted pairs contribute to these means; failed pairs remain "
                "in the table and raw files. Fewer selected test bins is better; higher fitness is better."
            ),
            "",
            "## Interpretation limits",
            "",
            (
                "This is a descriptive pilot. No p-value, statistical equivalence, or general discovery "
                "advantage is asserted. Exact reference matches are known; other novelty labels are "
                "unresolved. NSR and distinct verified mechanism yield are unavailable. More diverse "
                "probe behavior or different syntax does not establish a novel algorithm."
            ),
            "",
            (
                "Reproduce this report with `openend report RUN --output REPORT.md`. Recompute the "
                "saved evaluations with `openend replay RUN`; this makes no model calls."
            ),
            "",
        ]
    )
    return "\n".join(output)
