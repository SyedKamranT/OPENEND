"""Canonical, content-addressed experiment artifacts (never environment dumps)."""

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_manifest(root):
    """Capture actual source contents, including untracked work; exclude credentials."""
    root = Path(root).resolve()
    paths = [
        root / name for name in ("pyproject.toml", "README.md", "uv.lock", "requirements.lock")
    ]
    for folder, pattern in [("src/openend", "*.py"), ("configs", "*.json")]:
        paths.extend(sorted((root / folder).rglob(pattern)))
    hashes = {p.relative_to(root).as_posix(): file_hash(p) for p in paths if p.is_file()}
    command = ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root)]
    try:
        commit = subprocess.run(
            command + ["rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                command + ["status", "--porcelain"], capture_output=True, text=True, check=True
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {
        "git_commit": commit,
        "git_dirty": dirty,
        "files": hashes,
        "source_sha256": digest(hashes),
    }


def snapshot_source(root, manifest, destination):
    """Archive only explicitly allowlisted source files, never .env or run outputs."""
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, expected in manifest["files"].items():
            path = Path(root) / relative
            if file_hash(path) != expected:
                raise ValueError("source changed while snapshotting")
            archive.writestr(relative, path.read_bytes())
