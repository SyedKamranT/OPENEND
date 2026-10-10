import json
from pathlib import Path

import pytest

from openend.backends import OfflineBackend
from openend.experiment import load_config, replay_study, run_study
from openend.policy import REFERENCES, Policy
from openend.probes import build_panel_record, panel_from_record, saved_panel, validate_panel
from openend.search import PROBES, descriptor, signature

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_geometry_remains_numerically_identical():
    for policy in REFERENCES.values():
        sig = signature(policy)
        old = (
            sum((spaces[i] - item) / 100 for (item, spaces), i in zip(PROBES, sig)) / len(sig),
            sum(i / 5 for i in sig) / len(sig),
        )
        assert descriptor(sig) == old


def test_versioned_panel_distinguishes_exact_fit_and_normalizes_variable_bins():
    record = build_panel_record({"probe_panel": "training-mixed-v3"}, ROOT)
    panel = panel_from_record(record)
    assert len(panel) == 96 and panel[:32] == PROBES
    bonus = Policy.from_object({"expression": ["add", "gap", ["mul", 2, "exact_fit"]]})
    worst = REFERENCES["worst_fit"]
    assert signature(bonus) == signature(worst)
    assert sum(a != b for a, b in zip(signature(bonus, panel), signature(worst, panel))) == 32
    for policy in [*REFERENCES.values(), bonus]:
        assert all(0 <= x <= 1 for x in descriptor(signature(policy, panel), panel))
    assert descriptor((2,), ((50, (20, 40, 50)),)) == (0, 1)
    assert descriptor((0,), ((50, (50,)),)) == (0, 0)
    with pytest.raises(ValueError, match="feasible"):
        descriptor((0,), ((50, (20, 50)),))


@pytest.mark.parametrize(
    "panel", [[], [(50, [])], [(50, [20, 40])], [(True, [100])], [(50, [101])]]
)
def test_bad_probe_states_fail_before_search(panel):
    with pytest.raises(ValueError):
        validate_panel(panel)


def test_probe_artifact_is_pinned_and_cannot_silently_fall_back(tmp_path):
    folder = tmp_path / "data/benchmark"
    folder.mkdir(parents=True)
    path = folder / "training-probes-v3-candidate.json"
    data = json.loads((ROOT / "data/benchmark/training-probes-v3-candidate.json").read_text())
    data["rows"][0]["item"] += 1
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="frozen"):
        build_panel_record({"probe_panel": "training-mixed-v3"}, tmp_path)
    with pytest.raises(ValueError, match="missing"):
        saved_panel(tmp_path, {"probe_panel": "training-mixed-v3"})


def test_v3_replay_uses_saved_panel_without_workspace_artifact(tmp_path):
    folder = tmp_path / "data/benchmark"
    folder.mkdir(parents=True)
    panel_path = folder / "training-probes-v3-candidate.json"
    panel_path.write_bytes((ROOT / "data/benchmark/training-probes-v3-candidate.json").read_bytes())
    config = load_config(ROOT / "configs/local_probes_v3.json")
    config.update(seeds=[42], candidates_per_arm=2)
    output = tmp_path / "run"
    status, _ = run_study(config, OfflineBackend(), output, tmp_path)
    assert status == "completed"
    panel_path.write_text("workspace artifact changed after the run")
    assert replay_study(output)["replay"] == "matched"
    assert len(saved_panel(output, config)) == 96
