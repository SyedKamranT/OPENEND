"""Small CLI; API use is opt-in and logs contain no environment values."""

import argparse
import json
from pathlib import Path

from .artifacts import write_json
from .backends import APIBackend, OfflineBackend, settings
from .benchmark import make_suite, reference_scores, suite_record
from .experiment import load_config, replay_study, run_study, verify_artifacts
from .search import corpus_manifest


def main():
    parser = argparse.ArgumentParser(prog="openend")
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Check configuration presence, never credentials")
    doctor.add_argument("--env", default=".env")
    bench = sub.add_parser(
        "benchmark", help="Materialize deterministic pilot inputs and references"
    )
    bench.add_argument("--output", type=Path, required=True)
    bench.add_argument("--per-family", type=int, default=12)
    run = sub.add_parser("run", help="Run paired sparse-off/on pilot")
    run.add_argument("--config", default="configs/pilot.json", type=Path)
    run.add_argument("--backend", choices=["offline", "api"], default="offline")
    run.add_argument("--env", default=".env")
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--root", type=Path, default=Path.cwd())
    verify = sub.add_parser("verify", help="Check recorded input/output hashes")
    verify.add_argument("output", type=Path)
    replay = sub.add_parser("replay", help="Recompute saved candidate scores without model calls")
    replay.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "doctor":
        cfg = settings(args.env)
        print(json.dumps({key: bool(value) for key, value in cfg.items()}, indent=2))
    elif args.command == "benchmark":
        args.output.mkdir(parents=True, exist_ok=False)
        for split in ("train", "validation", "test"):
            write_json(args.output / f"{split}.json", suite_record(split, args.per_family))
            write_json(
                args.output / f"{split}_references.json",
                reference_scores(make_suite(split, args.per_family)),
            )
        write_json(args.output / "corpus_manifest.json", corpus_manifest())
        print(f"Benchmark written to {args.output}")
    elif args.command == "verify":
        print(json.dumps(verify_artifacts(args.output), indent=2))
    elif args.command == "replay":
        print(json.dumps(replay_study(args.output), indent=2))
    else:
        cfg = load_config(args.config)
        backend = (
            OfflineBackend()
            if args.backend == "offline"
            else APIBackend(args.env, cfg["max_output_tokens"], cfg["reasoning_effort"])
        )
        status, analysis = run_study(cfg, backend, args.output, args.root)
        print(json.dumps({"run_status": status, **analysis}, indent=2))
        if status != "completed":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
