# Local refinement findings — 2026-10-10

Phase 1 remains **open**. This is a development/calibration result, not a claim of novel invention or confirmation of OPENEND's broader hypothesis.

## What was wrong and what changed

The first local study's JSON mode enforced JSON syntax but not the expression language. It produced wrong-arity operators, expression strings, and four truncated responses. Its four-attempt arms also selected identical parents in every paired position. Those outcomes were inadequate for evaluating the sparse-selection mechanism.

The refinement introduces a finite schema, explicit syntax examples, and 16 attempts per arm across the same three seeds. Both arms receive the identical restricted proposal space (four operator levels, at most 31 nodes, seven numeric constants), fixed model/settings, and original evaluator. The sparse weights, benchmark, and utility threshold did not change. This bundles generation and budget refinements; comparisons with the earlier smoke test cannot isolate their separate causal effects.

The prospective [protocol](refined-pilot-protocol.md) was recorded before generation. One schema-compatibility attempt failed before inference; the corrected six-request training-only calibration passed 6/6. No calibration candidate seeded the experiment, no holdout was used for grammar tuning, and no failing response was silently repaired.

## Qwen 3.5 9B

The [full Qwen report](refined-qwen35-9b-results.md) records **96/96 valid policies**, 53,535 total tokens, and 584.0 seconds of request wall time. All 13 artifact checks passed; replay reproduced 96 scores and reconstructed selection probabilities, parents, and archives.

Sparse on/off selected different policy parents in **29/48** paired positions and different fixed-probe behaviors in **19/48** positions. The mean sparse selection distance from uniform was 0.0651 in total variation. Thus the treatment was exercised in this longer run.

Every selected test policy used **1,484 bins**. Utility-screen successes were zero in both arms. Mean sparse-on minus sparse-off coverage was **-0.009259**, or about **-0.93 percentage points**, with mixed signs across seeds. There is no measured quality advantage here; three seeds do not establish equivalence or general inefficacy.

## Independent-family replication

The prespecified Gemma 3 12B replication completed in `results/raw/local-gemma3-12b-refined-v2`; see the [full report](refined-gemma3-12b-results.md). All **96/96 policies were valid**. Usage was 56,344 tokens and 1,051.1 seconds of request wall time. Parent identities differed in **10/48** paired positions; probe behaviors differed in **8/48**. Mean sparse selection distance from uniform was 0.0897. All selected test policies again used 1,484 bins; no candidate passed the utility screen. Mean paired coverage difference was approximately -0.93 percentage points.

All 13 artifact checks passed and replay reproduced the 96 valid scores, selection probabilities, parent choices, and archives. Configuration, system-prompt, output-schema, and sampling-option comparisons matched Qwen; source snapshots differ only in report rendering. Qwen was unloaded before Gemma loaded, and Gemma was unloaded after completion. No cloud inference or downloads were used.

| Refined model | Valid attempts | Changed parents | Changed probe behaviors | Mean selected test-bin difference (on minus off) | Utility successes |
|---|---:|---:|---:|---:|---:|
| Qwen 3.5 9B | 96/96 | 29/48 | 19/48 | 0 | 0 |
| Gemma 3 12B | 96/96 | 10/48 | 8/48 | 0 | 0 |

The overall outcome is improved observed generation validity (192/192 in these refined runs, versus 14/24 in the original smoke test), an exercised treatment, and **no measured selected-policy quality advantage**. Neither statistical equivalence nor universal ineffectiveness follows from three search seeds per model on one development benchmark. Timings include different load/cache conditions and are operational observations, not controlled hardware performance comparisons.

## Interpretation and next decisions

### Concrete limitation in the original probe panel

The 32 fixed probes use item sizes 5–45 and six remaining capacities each in 46–100. Every bin is feasible and **zero probes offer an exact fit**. This is a representational limitation in the declared original panel, not a defect in the packing evaluator.

Counterexample: worst-fit (`"gap"`) and `["add","gap",["mul",2,"exact_fit"]]` have identical signatures across all 32 probes. For item 50 with remaining capacities `[60,50]`, worst-fit selects bin 0 while the bonus policy selects bin 1. Thus equal probe signatures do not imply behaviorally equivalent policies. The current targeting mechanism can miss a behavior difference relevant to packing.

In the completed Qwen run, 38 generated attempts matched worst-fit on these probes, 13 matched best-fit, two matched first-fit, and 43 matched none of those references. These are attempt counts and finite-probe matches, not novelty judgments or unique algorithm counts.

The fixed replication retains this panel. A subsequent protocol should build balanced probes from training-only trajectories and explicit boundary cases, including exact fits and mixed feasibility, with versioned handling of opening a new bin. Compare that representation change separately; do not replace the panel inside a running experiment or claim it will improve results before testing.

A concrete candidate artifact is now saved at `data/benchmark/training-probes-v3-candidate.json`. It contains 64 reachable training states: eight exact-fit and eight non-exact-fit choices per family. All have mixed feasibility and at least two feasible bins. Sampling seed 11007 and row provenance are recorded; tests replay the reference trajectories to verify reachability and balance. Forced placements are excluded because they cannot distinguish scoring policies. The counterexample differs on 32 of these states, versus zero original probes. This demonstrates coverage of the specific blind spot, not improved search utility.

The artifact is **not wired into the current experiment**. The original positional descriptor assumes six bins; a future integration must normalize by actual bin count, preserve appropriate synthetic decision cases, version the panel and descriptor, and record a new protocol before model generation. Generate the same candidate artifact with `python -m openend.probe_audit --output NEW_PATH.json`; existing files cannot be overwritten.

The engineering defect in policy serialization was actionable. A lack of positive objective results is not itself an implementation bug. Distinct expressions, different probes, more occupied cells, and model-generated text do not establish novel or useful algorithms.

After the fixed replications, examine generated training behaviors and the fixed-reference sparsity proxy before spending on larger searches. The current proxy measures distance relative to only three hand-coded references; it is not a literature novelty corpus or a validated notion of promising underexplored space. A stronger corpus and a theory-backed descriptor/targeting ablation are more defensible next research steps than adding a critic, choosing favorable seeds, changing the success threshold, or rerunning until positive.

Any revised mechanism needs a new prospective protocol and training-only development. Keep this inspected benchmark as development data and reserve a fresh holdout for eventual confirmation. Local raw results are ignored by Git; preserve their manifests, events, and source archives separately when transferring workspaces.

Final verification: **40 tests passed**, Ruff passed, both completed studies passed hash checks and full score/selection replay. The candidate probe artifact is covered by trajectory-reachability tests. No manuscript result claim or Phase 1 lock was introduced.
