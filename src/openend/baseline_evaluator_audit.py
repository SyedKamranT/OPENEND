"""Executable evaluator witnesses using reviewed, hash-pinned source fragments.

Requires NumPy in the audit environment. Never executes upstream imports, notebook
cells wholesale, or generated Python. This is not a generated-code sandbox.
"""

import __future__

import argparse
import ast
import json
import platform
from pathlib import Path
from types import SimpleNamespace

from .artifacts import file_hash
from .benchmark import Instance, reference_pack

PINS = {
    "eoh/src/eoh/problems/optimization/bp_online/run.py": "852dd811059e93904984a3b55f48682ec9f376bbbe36cc98108597ff537a4cc3",
    "bin_packing/bin_packing.ipynb": "eec45846a8661722addbb856179327cf2ede0bc502e32be4ad58a6ac54e0aca6",
}


def load_evaluators(root):
    import numpy as np

    folder = Path(root) / "data/baselines/evaluator-v1"
    manifest = json.loads((folder / "manifest.json").read_text())
    sources = {}
    for record in manifest["files"]:
        path = folder / record["local_path"]
        actual = file_hash(path)
        if actual != record["sha256"]:
            raise ValueError("evaluator source hash mismatch")
        if record["upstream_path"] in PINS:
            if actual != PINS[record["upstream_path"]]:
                raise ValueError("unreviewed evaluator source")
            sources[record["upstream_path"]] = path.read_text(encoding="utf-8")
    eoh = ast.parse(sources["eoh/src/eoh/problems/optimization/bp_online/run.py"])
    cls = next(n for n in eoh.body if isinstance(n, ast.ClassDef) and n.name == "BPONLINE")
    notebook = json.loads(sources["bin_packing/bin_packing.ipynb"])
    fun = ast.parse("".join(notebook["cells"][4]["source"]))

    def extract(nodes, names):
        selected = [n for n in nodes if isinstance(n, ast.FunctionDef) and n.name in names]
        if {n.name for n in selected} != set(names):
            raise ValueError("reviewed evaluator functions missing")
        scope = {"np": np}
        module = ast.Module(body=selected, type_ignores=[])
        code = compile(
            module, "<pinned-evaluator>", "exec", flags=__future__.annotations.compiler_flag
        )
        exec(code, scope)  # noqa: S102 - only reviewed methods from fixed source hashes
        return scope

    eoh_scope = extract(cls.body, ["get_valid_bin_indices", "online_binpack", "evaluateGreedy"])
    fun_scope = extract(fun.body, ["get_valid_bin_indices", "online_binpack", "evaluate"])
    # Bind only reviewed evaluator methods; BPONLINE.__init__/evaluate are never executed.
    host = SimpleNamespace()
    for name in ("get_valid_bin_indices", "online_binpack", "evaluateGreedy"):
        setattr(host, name, eoh_scope[name].__get__(host))
    return host, fun_scope


def audit(root):
    import numpy as np

    eoh, fun = load_evaluators(root)
    policies = {
        "first_fit": lambda item, bins: np.zeros(len(bins)),
        "best_fit": lambda item, bins: -(bins - item),
        "worst_fit": lambda item, bins: bins - item,
    }
    rows = []
    for items in ((40, 40, 20), (60, 40), (60, 60), (100,), (25, 25, 25, 25)):
        instance = Instance("audit/witness", "diagnostic", 100, items)
        for name, score in policies.items():
            fun["priority"] = score
            counts = {}
            for method in ("eoh", "funsearch"):
                bins = np.full(len(items), 100)
                if method == "eoh":
                    _, remaining = eoh.online_binpack(items, bins, SimpleNamespace(score=score))
                else:
                    _, remaining = fun["online_binpack"](items, bins)
                counts[method] = int((remaining != 100).sum())
            rows.append(
                {
                    "items": list(items),
                    "policy": name,
                    "openend_bins": reference_pack(name, instance)[0],
                    **counts,
                }
            )

    def dataset(items):
        return {"fixture": {"capacity": 100, "items": items, "num_items": len(items)}}

    a, b = dataset((40, 40, 20)), dataset((60, 60))
    eoh.lb = {"a": 1, "b": 1}
    objectives = {}
    for order in (("a", "b"), ("b", "a")):
        eoh.instances = {key: {"a": a, "b": b}[key] for key in order}
        objectives["_then_".join(order)] = float(
            eoh.evaluateGreedy(SimpleNamespace(score=policies["best_fit"]))
        )
    fun["priority"] = policies["best_fit"]
    combined = {"a": a["fixture"], "b": b["fixture"]}
    return {
        "schema_version": 1,
        "scope": "deterministic evaluator witnesses; no generated code or model calls",
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "sources": PINS,
        "source_manifest_sha256": file_hash(
            Path(root) / "data/baselines/evaluator-v1/manifest.json"
        ),
        "audit_implementation_sha256": file_hash(Path(__file__)),
        "packing_witnesses": rows,
        "eoh_last_dataset_objectives": objectives,
        "eoh_fixture_lower_bounds": eoh.lb,
        "funsearch_negative_mean_bins": float(fun["evaluate"](combined)),
        "openend_total_bins": 3,
        "limitations": [
            "Fixtures are not performance evidence.",
            "Native generated-code execution and containment remain unimplemented.",
            "Injected EoH bounds demonstrate aggregation, not the upstream data loader.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(f"Saved {len(result['packing_witnesses'])} evaluator witnesses to {args.output}")


if __name__ == "__main__":
    main()
