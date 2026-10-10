# Bin-packing pilot results

Run: `results/raw/offline-pilot-final`. Status: **completed**.
Backend: `offline`; model: `seeded-tree-mutation-v1`.

Recorded attempt events: **400**. Status counts: `{'ok': 400}`.
Provider-reported total tokens: **0** (unknown usage is not imputed as free).
The offline backend makes no API calls. Setup reference evaluations are separate.

Both arms use identical configured allowances, initial references, QD grid, probes, and evaluator. Parent-selection weights are the treatment. Seeds replicate search on one fixed benchmark; they do not replicate independent task families.

| Seed | Arm | Valid / attempts | Coverage | Selected test bins | Utility successes | Stop |
|---:|---|---:|---:|---:|---:|---|
| 42 | sparse_off | 40 / 40 | 0.1389 | 1484 | 0 | candidate_limit |
| 42 | sparse_on | 40 / 40 | 0.1389 | 1484 | 0 | candidate_limit |
| 137 | sparse_off | 40 / 40 | 0.2222 | 1484 | 0 | candidate_limit |
| 137 | sparse_on | 40 / 40 | 0.2222 | 1484 | 0 | candidate_limit |
| 2024 | sparse_off | 40 / 40 | 0.1667 | 1484 | 0 | candidate_limit |
| 2024 | sparse_on | 40 / 40 | 0.1389 | 1484 | 0 | candidate_limit |
| 4096 | sparse_off | 40 / 40 | 0.1111 | 1484 | 0 | candidate_limit |
| 4096 | sparse_on | 40 / 40 | 0.1111 | 1484 | 0 | candidate_limit |
| 8192 | sparse_off | 40 / 40 | 0.1667 | 1484 | 0 | candidate_limit |
| 8192 | sparse_on | 40 / 40 | 0.1667 | 1484 | 0 | candidate_limit |

Selection uses training fitness only. All generation ends before held-out scoring. Utility success is the predeclared 1% aggregate improvement / 5% family-regression screen.

## Paired differences (sparse on minus off)

- `utility_success_rate`: `0.0`
- `coverage`: `-0.005555555555555552`
- `selected_test_bins`: `0`
- `selected_test_fitness`: `0.0`

Only complete, usage-accounted pairs contribute to these means; failed pairs remain in the table and raw files. Fewer selected test bins is better; higher fitness is better.

## Interpretation limits

This is a descriptive pilot. No p-value, statistical equivalence, or general discovery advantage is asserted. Exact reference matches are known; other novelty labels are unresolved. NSR and distinct verified mechanism yield are unavailable. More diverse probe behavior or different syntax does not establish a novel algorithm.

Reproduce this report with `openend report RUN --output REPORT.md`. Recompute the saved evaluations with `openend replay RUN`; this makes no model calls.
