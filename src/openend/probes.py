"""Versioned, hash-pinned behavioral probes, independent of model output."""

import json
from pathlib import Path

from .artifacts import digest
from .search import PROBES

TRAINING_SHA256 = "4548ba0b95d0be0d039282ee9f01d069475d6c8fa6bec90a08f1e025f73c51d7"
PANEL_VERSIONS = ("legacy-v1", "training-mixed-v3")


def validate_panel(value):
    if not isinstance(value, (tuple, list)) or not value:
        raise ValueError("empty or invalid probe panel")
    panel = []
    for row in value:
        if not isinstance(row, (tuple, list)) or len(row) != 2:
            raise ValueError("invalid probe row")
        item, spaces = row
        if (
            type(item) is not int
            or not 1 <= item <= 100
            or not isinstance(spaces, (tuple, list))
            or not 1 <= len(spaces) <= 1000
            or any(type(space) is not int or not 0 <= space <= 100 for space in spaces)
            or not any(space >= item for space in spaces)
        ):
            raise ValueError("probe must contain valid capacities and a feasible choice")
        panel.append((item, tuple(spaces)))
    return tuple(panel)


def build_panel_record(config, root):
    version = config.get("probe_panel", "legacy-v1")
    if version not in PANEL_VERSIONS:
        raise ValueError("unknown probe panel version")
    panel = PROBES
    provenance = None
    if version == "training-mixed-v3":
        path = Path(root) / "data/benchmark/training-probes-v3-candidate.json"
        provenance = json.loads(path.read_text(encoding="utf-8"))
        if (
            provenance.get("split") != "train"
            or provenance.get("sha256") != TRAINING_SHA256
            or digest(provenance.get("rows")) != TRAINING_SHA256
        ):
            raise ValueError("training probe artifact does not match the frozen version")
        if any(
            row["capacity"] != 100 or not row["instance_id"].startswith("train/")
            for row in provenance["rows"]
        ):
            raise ValueError("probe provenance must be training-only at capacity 100")
        panel = PROBES + tuple((row["item"], tuple(row["remaining"])) for row in provenance["rows"])
    panel = validate_panel(panel)
    return {
        "version": version,
        "descriptor": "mean-residual-and-relative-bin-position",
        "capacity": 100,
        "panel": panel,
        "sha256": digest(panel),
        "training_provenance": provenance,
    }


def panel_from_record(record):
    if record.get("version") not in PANEL_VERSIONS or record.get("capacity") != 100:
        raise ValueError("unknown recorded representation")
    panel = validate_panel(record["panel"])
    if digest(panel) != record.get("sha256"):
        raise ValueError("probe content hash mismatch")
    return panel


def saved_panel(output, config):
    path = Path(output) / "probe_panel.json"
    if path.exists():
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["version"] != config.get("probe_panel", "legacy-v1"):
            raise ValueError("saved probe version differs from configuration")
        return panel_from_record(record)
    if config.get("probe_panel", "legacy-v1") != "legacy-v1":
        raise ValueError("versioned run is missing its probe artifact")
    return PROBES
