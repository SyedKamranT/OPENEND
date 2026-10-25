from openend.benchmark import Instance
from openend.coordinated_sketch import plan, trace_effect
from openend.decision_diagnostic import trace
from openend.policy import REFERENCES, Policy


def test_zero_weight_is_best_fit_and_plan_is_bounded():
    rows = plan()
    assert len(rows) == 69
    for row in rows:
        policy = Policy.from_object({"expression": row["expression"]})
        if row.get("weight") == 0:
            for item in range(1, 11):
                for spaces in ([1, 5, 10], [10, 5, 5], [], [1, 2]):
                    assert policy.choose(item, spaces, 10) == REFERENCES["best_fit"].choose(
                        item, spaces, 10
                    )


def test_trace_effect_identifies_known_beneficial_action():
    # Moving 30 into the 50-space bin preserves 40 for the final item.
    instance = Instance("fixture", "uniform", 100, (60, 50, 30, 20, 40))
    traces = [trace(instance)]
    bf = trace_effect(REFERENCES["best_fit"], traces)
    wf = trace_effect(REFERENCES["worst_fit"], traces)
    assert bf["beneficial"] == bf["harmful"] == 0
    assert wf["beneficial"] == 1
    assert wf["corrected_opportunities"] == 1
