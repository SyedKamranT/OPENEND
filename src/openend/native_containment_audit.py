"""Fixed adversarial probes for the restricted native container launcher."""

import argparse
from pathlib import Path

from .artifacts import file_hash, write_json
from .native_container import execute

BF = "def score(item, bins):\n    return -(bins-item)\n"


def cases():
    return [
        ("best_fit", BF, "completed", 1),
        ("worst_fit", "def score(item,bins):\n    return bins-item\n", "completed", 3),
        (
            "root_readonly",
            "try:\n    open('/forbidden','w')\nexcept OSError:\n    pass\nelse:\n    raise AssertionError('root writable')\n"
            + BF,
            "completed",
            1,
        ),
        (
            "network_none",
            "import socket\ns=socket.socket()\ns.settimeout(1)\ntry:\n    s.connect(('198.51.100.1',80))\nexcept OSError:\n    pass\nelse:\n    raise AssertionError('external connection')\nfinally:\n    s.close()\nassert len(socket.if_nameindex()) == 1\n"
            + BF,
            "completed",
            1,
        ),
        (
            "kernel_limits",
            "import os\nassert os.getuid()==65534\ns=dict(line.split(':',1) for line in open('/proc/self/status') if ':' in line)\nassert int(s['CapEff'].strip(),16)==0\nassert s['NoNewPrivs'].strip()=='1'\nassert s['Seccomp'].strip()=='2'\nassert int(open('/sys/fs/cgroup/memory.max').read())==268435456\nassert int(open('/sys/fs/cgroup/pids.max').read())==32\nassert not os.path.exists('/var/run/docker.sock')\n"
            + BF,
            "completed",
            1,
        ),
        ("infinite_loop", "while True: pass\n" + BF, "timeout", None),
        (
            "output_flood",
            "import os\nwhile True: os.write(1,b'x'*4096)\n" + BF,
            "output_limit",
            None,
        ),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--docker", required=True)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    inputs = [
        "docs/native-containment-v1-protocol.md",
        "native_runtime/Dockerfile",
        "native_runtime/worker.py",
        "src/openend/native_container.py",
        "src/openend/native_containment_audit.py",
    ]
    for name in inputs:
        target = args.output / "snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(Path(name).read_bytes())
    rows = []
    for name, code, expected, bins in cases():
        payload = {
            "code": code,
            "function": "score",
            "instances": [
                {
                    "instance_id": "native/witness",
                    "family": "fixture",
                    "capacity": 100,
                    "items": [40, 40, 20],
                }
            ],
        }
        try:
            result = execute(args.docker, args.image, payload, timeout=10)
            passed = result["status"] == expected and result["cleanup_verified"]
            if bins is not None:
                passed = (
                    passed
                    and result.get("evaluation", {}).get("instances", [{}])[0].get("bins") == bins
                )
        except Exception as exc:  # noqa: BLE001 - preserve a failed audit, never infer success
            result, passed = {"error": type(exc).__name__, "message": str(exc)}, False
        rows.append(
            {
                "case": name,
                "code": code,
                "expected_status": expected,
                "passed": passed,
                "result": result,
            }
        )
        write_json(
            args.output / "report.json",
            {
                "image": args.image,
                "complete": len(rows) == len(cases()),
                "passed": len(rows) == len(cases()) and all(r["passed"] for r in rows),
                "cases": rows,
                "model_calls": 0,
            },
        )
        print(name, passed, flush=True)
    write_json(
        args.output / "manifest.json",
        {
            "files": {
                p.relative_to(args.output).as_posix(): file_hash(p)
                for p in args.output.rglob("*")
                if p.is_file()
            }
        },
    )


if __name__ == "__main__":
    main()
