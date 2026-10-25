from openend.benchmark_diagnostics import panel_report, policies, stress_panel
from openend.policy import Policy
from openend.search import PROBES
from openend.utility_runner import parse


def test_stress_panels_are_reproducible_feasible_and_have_boundary_cases():
    panel = stress_panel(2026101501)
    assert panel == stress_panel(2026101501)
    assert panel != stress_panel(2026101502)
    assert len(panel) == 96
    assert all(len(spaces) == 6 and max(spaces) >= item for item, spaces in panel)
    assert all(item in spaces for item, spaces in panel[32:64])
    assert all(min(spaces) < item <= max(spaces) for item, spaces in panel[64:])


def test_new_panel_exposes_legacy_collision_without_changing_search_panel():
    candidates = {
        "constant": Policy.from_object({"expression": 0}),
        "exact": Policy.from_object({"expression": "exact_fit"}),
    }
    legacy = panel_report(PROBES, candidates)
    stress = panel_report(stress_panel(2026101501), candidates)
    assert legacy["pairwise_disagreement"][0]["distance"] == 0
    assert stress["pairwise_disagreement"][0]["distance"] > 0
    assert legacy["collision_groups"] == [["constant", "exact"]]
    assert stress["collision_groups"] == []


def test_fixed_candidates_all_fit_the_actual_proposal_language():
    import json

    for policy in policies().values():
        assert parse(json.dumps(policy.to_object())) == policy
