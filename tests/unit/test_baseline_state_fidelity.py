"""Execute only reviewed hash-pinned methods, with model/evaluator calls replaced by fixtures."""

import copy
import json
from types import SimpleNamespace

from openend.baseline_mechanics import eoh_survivors, funsearch_reduced_score, funsearch_signature
from openend.baseline_state import EohState, FunsearchState
from tests.unit.test_baseline_mechanics import upstream

EOH = "eoh/src/eoh/methods/eoh/eoh.py"
INTERFACE = "eoh/src/eoh/methods/eoh/eoh_interface_EC.py"
FUN = "implementation/programs_database.py"


def test_eoh_initialization_and_population_updates_match_pinned_main_loop(tmp_path):
    size = 4
    # Include objective ties and failures; no program generation or evaluation occurs.
    scores = [8, 3, 3, None, 7, 4, 2, 9] + [5, 2, 1, None] * 8
    proposals = [{"id": i, "objective": score} for i, score in enumerate(scores)]
    batches = []

    class Interface:
        position = 0

        def get_algorithm(self, population, operator):
            batches.append((operator, copy.deepcopy(population)))
            batch = copy.deepcopy(proposals[self.position : self.position + size])
            self.position += size
            return [], batch

        population_generation = upstream(INTERFACE, "InterfaceEC.population_generation")

    interface = Interface()
    namespace = {
        "InterfaceEC": lambda *args, **kwargs: interface,
        "np": SimpleNamespace(random=SimpleNamespace(rand=lambda: 0.0)),
        "time": SimpleNamespace(time=lambda: 0),
        "json": json,
    }
    run = upstream(EOH, "EOH.run", namespace)
    engine = SimpleNamespace(
        prob=None,
        pop_size=size,
        m=2,
        api_endpoint=None,
        api_key=None,
        llm_model=None,
        use_local_llm=False,
        llm_local_url=None,
        debug_mode=False,
        select=None,
        exp_n_proc=1,
        timeout=1,
        use_numba=False,
        use_seed=False,
        load_pop=False,
        output_path=str(tmp_path),
        n_pop=2,
        operators=["e1", "e2", "m1", "m2"],
        operator_weights=[1, 1, 1, 1],
        manage=SimpleNamespace(
            population_management=upstream(
                "eoh/src/eoh/methods/management/pop_greedy.py",
                "population_management",
                {"heapq": __import__("heapq")},
            )
        ),
    )
    add = upstream(EOH, "EOH.add2pop")
    engine.add2pop = lambda population, offspring: add(engine, population, offspring)
    (tmp_path / "results/pops").mkdir(parents=True)
    (tmp_path / "results/pops_best").mkdir()
    run(engine)
    assert [op for op, _ in batches] == ["i1", "i1", "e1", "e2", "m1", "m2", "e1", "e2", "m1", "m2"]
    state = EohState(size, 42)
    for index, proposal in enumerate(proposals):
        request = state.request()
        batch_index = index // size
        assert request["operator"] == batches[batch_index][0]
        assert state.population == batches[batch_index][1]
        state.observe(request, proposal if proposal["objective"] is not None else None)
    saved_final = json.loads((tmp_path / "results/pops/population_generation_2.json").read_text())
    assert state.population == saved_final
    assert state.population == eoh_survivors(proposals, size)


def test_funsearch_registration_matches_upstream_signature_groups_and_best():
    cluster_init = upstream(FUN, "Cluster.__init__")
    cluster_register = upstream(FUN, "Cluster.register_program")

    class Cluster:
        __init__ = cluster_init
        register_program = cluster_register

    register = upstream(
        FUN,
        "Island.register_program",
        {
            "_get_signature": funsearch_signature,
            "_reduce_score": funsearch_reduced_score,
            "Cluster": Cluster,
        },
    )
    upstream_island = SimpleNamespace(_clusters={}, _num_programs=0)
    local = FunsearchState.new_island()
    # Distinct signatures can have equal totals; duplicate programs still register.
    scores = [
        {"a": -2, "b": -3, "aggregate": -5},
        {"a": -3, "b": -2, "aggregate": -5},
        {"a": -2, "b": -3, "aggregate": -5},
        {"a": -1, "b": -2, "aggregate": -3},
    ]
    for index, score in enumerate(scores):
        program = {"id": index, "scores": score, "objective": -score["aggregate"]}
        register(upstream_island, program, score)
        FunsearchState.register(local, program)
        assert local["registrations"] == upstream_island._num_programs
        assert {
            key: cluster._programs for key, cluster in upstream_island._clusters.items()
        } == local["clusters"]
    assert local["best"]["id"] == 3


def test_funsearch_database_best_replacement_matches_upstream_and_keeps_ties():
    island = FunsearchState.new_island()
    stored = []
    database = SimpleNamespace(
        _islands=[SimpleNamespace(register_program=lambda program, scores: stored.append(program))],
        _best_score_per_island=[float("-inf")],
        _best_program_per_island=[None],
        _best_scores_per_test_per_island=[None],
    )
    register = upstream(
        FUN,
        "ProgramsDatabase._register_program_in_island",
        {
            "_reduce_score": funsearch_reduced_score,
            "logging": SimpleNamespace(info=lambda *args: None),
        },
    )
    for index, total in enumerate([10, 10, 12, 8, 8]):
        program = {"id": index, "objective": total, "scores": {"aggregate": -total}}
        register(database, program, 0, program["scores"])
        FunsearchState.register(island, program)
        assert island["best"] == database._best_program_per_island[0]
    assert island["best"]["id"] == 3 and len(stored) == 5
