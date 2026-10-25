"""Numerical differential audit of reviewed pinned FunSearch sampling functions."""

import __future__

import argparse
import ast
import platform
from pathlib import Path
from types import SimpleNamespace

from .artifacts import file_hash, write_json
from .baseline_mechanics import funsearch_length_probabilities, funsearch_temperature, softmax

PIN = "b2bef312d04861f467f304f65788efe959f0493818976b052c46b4703151affc"
SOURCE = "data/baselines/upstream-v1/funsearch/implementation__programs_database.py.txt"


def audit(root):
    import numpy as np
    import scipy
    import scipy.special

    path = Path(root) / SOURCE
    if file_hash(path) != PIN:
        raise ValueError("unreviewed source hash")
    tree = ast.parse(path.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_softmax")
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Cluster")
    sample = next(
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "sample_program"
    )
    scope = {"np": np, "scipy": scipy}
    exec(  # noqa: S102 - fixed reviewed functions only
        compile(
            ast.Module(body=[function, sample], type_ignores=[]),
            str(path),
            "exec",
            flags=__future__.annotations.compiler_flag,
        ),
        scope,
    )
    rows = []
    for dtype in (np.int64, np.float32, np.float64):
        for scores in (
            [0, 0, 0],
            [-1476, -1475, -1474],
            [-1000000, 0, 1000000],
            [16777216, 16777217, 16777218],
        ):
            for registrations in (0, 15000, 29999, 30000):
                temperature = funsearch_temperature(registrations)
                values = np.array(scores, dtype=dtype)
                upstream = scope["_softmax"](values, temperature).tolist()
                local = softmax(values.tolist(), temperature)
                rows.append(
                    {
                        "dtype": str(values.dtype),
                        "scores": values.tolist(),
                        "registrations": registrations,
                        "temperature": temperature,
                        "upstream": upstream,
                        "adapted": local,
                        "max_abs_difference": max(abs(a - b) for a, b in zip(upstream, local)),
                    }
                )
    lengths = []

    class Capture:
        def __getattr__(self, name):
            return getattr(np, name)

        random = SimpleNamespace(choice=lambda programs, p: p.tolist())

    scope["np"] = Capture()
    for sizes in ([0], [0, 0], [1, 10, 100], [10, 10, 10], [100, 101, 10000]):
        probabilities = scope["sample_program"](
            SimpleNamespace(_lengths=sizes, _programs=list(range(len(sizes))))
        )
        local = funsearch_length_probabilities(sizes)
        lengths.append(
            {
                "lengths": sizes,
                "upstream": probabilities,
                "adapted": local,
                "max_abs_difference": max(abs(a - b) for a, b in zip(probabilities, local)),
            }
        )
    total = [-1476, -1475, -1474]
    scale = {
        "total_bins": softmax(total, 0.1),
        "mean_bins": softmax([x / 48 for x in total], 0.1),
        "total_with_scaled_temperature": softmax(total, 4.8),
    }
    return {
        "source_sha256": PIN,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "probability_cases": rows,
        "length_cases": lengths,
        "score_scale_witness": scale,
        "model_calls": 0,
        "limitation": "Numerical fixtures only; RNG streams and full native algorithm not reproduced.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path.cwd()
    report = audit(root)
    for name in (
        SOURCE,
        "src/openend/baseline_probability_audit.py",
        "src/openend/baseline_mechanics.py",
    ):
        target = args.output / "snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / name).read_bytes())
    write_json(args.output / "report.json", report)
    write_json(
        args.output / "manifest.json",
        {
            "status": "completed",
            "files": {
                p.relative_to(args.output).as_posix(): file_hash(p)
                for p in args.output.rglob("*")
                if p.is_file()
            },
        },
    )
    print(
        {
            "cases": len(report["probability_cases"]),
            "length_cases": len(report["length_cases"]),
            "max_difference": max(x["max_abs_difference"] for x in report["probability_cases"]),
            "scale": report["score_scale_witness"],
        }
    )


if __name__ == "__main__":
    main()
