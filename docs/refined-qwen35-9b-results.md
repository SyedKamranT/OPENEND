# Bin-packing pilot results

Run: `results/raw/local-qwen35-9b-refined-v2`. Status: **completed**.
Backend: `local`; model: `qwen3.5:9b`.

Recorded attempt events: **96**. Status counts: `{'ok': 96}`.
Provider-reported total tokens: **53535** (unknown usage is not imputed as free).
Setup reference evaluations are separate from generated attempts.
Recorded request wall time: 584.0 seconds (when supplied by the backend).
Generated tokens: 1827; recorded generation time: 316.9 seconds.
Different selected parents at paired attempt positions: **29/48**.
If no paired parents differ, this run does not exercise different parent choices.
Different parent probe behaviors at paired positions: **19/48**.
Mean sparse-arm selection total variation from uniform: `0.06514133622445752`.

Both arms use identical configured allowances, initial references, QD grid, probes, and evaluator. Parent-selection weights are the treatment. Seeds replicate search on one fixed benchmark; they do not replicate independent task families.

| Seed | Arm | Valid / attempts | Unique syntax / probes | Coverage | Selected test bins | Utility successes | Stop |
|---:|---|---:|---:|---:|---:|---:|---|
| 42 | sparse_off | 16 / 16 | 13 / 6 | 0.1667 | 1484 | 0 | candidate_limit |
| 42 | sparse_on | 16 / 16 | 9 / 5 | 0.1111 | 1484 | 0 | candidate_limit |
| 137 | sparse_off | 16 / 16 | 7 / 3 | 0.0833 | 1484 | 0 | candidate_limit |
| 137 | sparse_on | 16 / 16 | 6 / 4 | 0.1389 | 1484 | 0 | candidate_limit |
| 2024 | sparse_off | 16 / 16 | 12 / 8 | 0.1667 | 1484 | 0 | candidate_limit |
| 2024 | sparse_on | 16 / 16 | 11 / 8 | 0.1389 | 1484 | 0 | candidate_limit |

Selection uses training fitness only. All generation ends before held-out scoring. Utility success is the predeclared 1% aggregate improvement / 5% family-regression screen.

## Paired differences (sparse on minus off)

- `utility_success_rate`: `0.0`
- `coverage`: `-0.00925925925925925`
- `selected_test_bins`: `0`
- `selected_test_fitness`: `0.0`

Only complete, usage-accounted pairs contribute to these means; failed pairs remain in the table and raw files. Fewer selected test bins is better; higher fitness is better.

## Interpretation limits

This is a descriptive pilot. No p-value, statistical equivalence, or general discovery advantage is asserted. Exact reference matches are known; other novelty labels are unresolved. NSR and distinct verified mechanism yield are unavailable. More diverse probe behavior or different syntax does not establish a novel algorithm.

Reproduce this report with `openend report RUN --output REPORT.md`. Recompute the saved evaluations with `openend replay RUN`; this makes no model calls.
