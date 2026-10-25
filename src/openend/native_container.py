"""Bounded container transport; never executes candidate Python on the host."""

import json
import re
import subprocess
import threading
import time
import uuid

from .benchmark import Instance, check_certificate


def command(docker, image, name):
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
        raise ValueError("resolved image ID required")
    return [
        docker,
        "run",
        "--rm",
        "--name",
        name,
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--user",
        "65534:65534",
        "--pids-limit",
        "32",
        "--memory",
        "256m",
        "--memory-swap",
        "256m",
        "--cpus",
        "1",
        "--ulimit",
        "nofile=64:64",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,nodev,size=16m",
        "--log-driver",
        "none",
        "-i",
        image,
    ]


def execute(docker, image, payload, timeout=10, output_limit=131072):
    if not 0 < timeout <= 60 or not 0 < output_limit <= 1048576:
        raise ValueError("invalid execution bounds")
    raw = json.dumps(payload, allow_nan=False).encode()
    if len(raw) > 65536:
        raise ValueError("payload too large")
    name = "openend-native-" + uuid.uuid4().hex
    args = command(docker, image, name)
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    exceeded = threading.Event()
    lock = threading.Lock()
    process = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    def read(stream, key):
        while True:
            block = stream.read(4096)
            if not block:
                break
            with lock:
                available = max(0, output_limit - sum(len(x) for x in buffers.values()))
                buffers[key].extend(block[:available])
                if len(block) > available:
                    exceeded.set()

    def write():
        try:
            process.stdin.write(raw)
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass

    threads = [
        threading.Thread(target=read, args=(process.stdout, "stdout"), daemon=True),
        threading.Thread(target=read, args=(process.stderr, "stderr"), daemon=True),
        threading.Thread(target=write, daemon=True),
    ]
    for thread in threads:
        thread.start()
    start = time.monotonic()
    status = "completed"
    cleanup = None
    try:
        while process.poll() is None:
            if exceeded.is_set():
                status = "output_limit"
                break
            if time.monotonic() - start >= timeout:
                status = "timeout"
                break
            time.sleep(0.02)
    finally:
        # Kill by unique container name, not merely the CLI process.
        try:
            cleanup = subprocess.run(
                [docker, "rm", "-f", name], capture_output=True, timeout=15, check=False
            )
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            for thread in threads:
                thread.join(timeout=1)
    if exceeded.is_set():
        status = "output_limit"
    elif status == "completed" and process.returncode != 0:
        status = "candidate_or_runtime_error"
    # Nonzero rm is expected if --rm already removed a successfully exited container.
    remaining = subprocess.run(
        [docker, "ps", "-aq", "--filter", "name=^/" + name + "$"],
        capture_output=True,
        timeout=10,
        check=False,
    )
    if remaining.returncode or remaining.stdout.strip():
        raise RuntimeError("container cleanup not verified")
    result = {
        "status": status,
        "exit_code": process.returncode,
        "cleanup_verified": True,
        "stdout": buffers["stdout"].decode(errors="replace"),
        "stderr": buffers["stderr"].decode(errors="replace"),
        "wall_seconds": time.monotonic() - start,
        "image": image,
        "cleanup_exit_code": cleanup.returncode,
    }
    if status == "completed":
        parsed = json.loads(result["stdout"])
        expected = payload["instances"]
        rows = parsed["instances"]
        if len(rows) != len(expected):
            raise ValueError("incomplete native evaluation")
        for instance, row in zip(expected, rows):
            if row["instance_id"] != instance["instance_id"]:
                raise ValueError("instance mismatch")
            count = check_certificate(
                Instance(**{**instance, "items": tuple(instance["items"])}), row["assignments"]
            )
            row["bins"] = count
        result["evaluation"] = parsed
    return result
