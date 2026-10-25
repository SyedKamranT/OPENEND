# Phase 3 closure — bounded development benchmark v1

**Status: CLOSED for the development benchmark contract, 2026-10-15.**
This accepts a reproducible measurement system with documented limits. It does not
establish useful improvement, a general-purpose benchmark, or readiness for confirmation.
The [benchmark contract](phase3-benchmark-contract-v1.md) defines the accepted behavior.

| Acceptance requirement | Evidence / decision |
|---|---|
| Problem, objective, constraints and references | Capacity-100 online packing contract, total-bin objective, First/Best/Worst Fit |
| Host and certificate correctness | 816 reference comparisons; five host fixtures; exhaustive tiny-stream and invalid-certificate unit tests |
| Numerical and representation semantics | `test_benchmark.py`, finite-grammar diagnostics, numerical audit and [rewrite sensitivity](representation-v2-results.md) |
| Data boundaries | Development-block role separation tests, hashes and duplicate checks on acceptance fixtures; public data remain development |
| Selection before evaluation | Utility/block integration tests and saved-response replay, with committed selected-policy hashes |
| Resources and failures | Existing usage/status tests, missing-outcome bounds tests and preservation of interrupted baseline evidence |
| Descriptor robustness | [Three-panel sensitivity audit](phase3-diagnostics-v1-results.md); dependence and residual collisions disclosed |
| Useful signal | Historical small gain reproduced; 1% screen remains unmet by fixed candidates; no full-language impossibility claim |
| Novelty interpretation | Known-reference controls and unresolved labels; frozen corpus unchanged; descriptors cannot certify novelty |
| Reproducibility | Release manifest and source/contract/evidence snapshot under `results/raw/phase3-benchmark-release-v1` |

## What proceeds next

Phase 4 is active for baseline implementation/protocol preparation. The comparator
obligations from the reviewed Phase 2 assessment remain. Before a large model-backed
comparison, prospectively address the lack of a useful-gain witness and justify the
intended effect scale. Engineering trials must be named as such. Do not lower the 1%
screen after observing these results or infer equivalence from zero differences.

The primary search panel, interpreter, datasets and historical outcomes are unchanged.
A richer representation or different panel is a new version, with training-only diagnostic
selection and later fresh evaluation. Final inferential calibration and holdout access
remain Phase 13 entry conditions, not claimed accomplishments here.

This closes the benchmark construction and diagnostic assessment. Negative diagnostic
outcomes are part of the accepted release, not requirements to hide or keep searching
until a favorable answer appears.

Validation at closure: **133 tests passed in 38.09s; Ruff clean.** Saved-response replay matched all 240 utility attempts and 640 development-block attempts. No model calls were made.
