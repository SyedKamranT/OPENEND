from openend.benchmark_acceptance import audit, probe_coverage


def test_acceptance_checks_and_probe_counterexample():
    report = audit()
    assert report["reference_comparisons"] == 816
    assert report["distinct_development_streams"] == 16
    assert all(case["passed"] for case in report["host_contract_cases"])
    assert report["legacy_probe_coverage"] == {
        "states": 32,
        "exact_fit_states": 0,
        "mixed_feasibility_states": 0,
        "no_feasible_bin_states": 0,
        "all_feasible_states": 32,
    }
    witness = report["blind_spot_witness"]
    assert witness["legacy_signatures_equal"]
    assert witness["choices"] == [0, 1]
    # Known policies can have nonzero reference distance: it cannot certify novelty.
    assert any(value > 0 for value in report["reference_distances"].values())


def test_coverage_counts_distinguish_host_branches():
    coverage = probe_coverage(((40, (80, 40)), (40, (20, 60)), (60, (40, 50))))
    assert coverage == {
        "states": 3,
        "exact_fit_states": 1,
        "mixed_feasibility_states": 1,
        "no_feasible_bin_states": 1,
        "all_feasible_states": 1,
    }
