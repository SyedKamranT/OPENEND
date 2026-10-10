# Bin-packing pilot results

Run: `results/raw/local-qwen35-9b-v1`. Status: **completed**.
Backend: `local`; model: `qwen3.5:9b`.

Recorded attempt events: **24**. Status counts: `{'incomplete_response': 4, 'invalid_policy': 6, 'ok': 14}`.
Provider-reported total tokens: **11430** (unknown usage is not imputed as free).
Setup reference evaluations are separate from generated attempts.
Recorded request wall time: 491.2 seconds (when supplied by the backend).
Generated tokens: 2318; recorded generation time: 435.9 seconds.
Different selected parents at paired attempt positions: **0/12**.
If no paired parents differ, this run does not exercise different parent choices.

Both arms use identical configured allowances, initial references, QD grid, probes, and evaluator. Parent-selection weights are the treatment. Seeds replicate search on one fixed benchmark; they do not replicate independent task families.

| Seed | Arm | Valid / attempts | Coverage | Selected test bins | Utility successes | Stop |
|---:|---|---:|---:|---:|---:|---|
| 42 | sparse_off | 2 / 4 | 0.0833 | 1484 | 0 | candidate_limit |
| 42 | sparse_on | 2 / 4 | 0.0833 | 1484 | 0 | candidate_limit |
| 137 | sparse_off | 3 / 4 | 0.0833 | 1485 | 0 | candidate_limit |
| 137 | sparse_on | 3 / 4 | 0.0833 | 1485 | 0 | candidate_limit |
| 2024 | sparse_off | 2 / 4 | 0.0833 | 1536 | 0 | candidate_limit |
| 2024 | sparse_on | 2 / 4 | 0.0833 | 1536 | 0 | candidate_limit |

Selection uses training fitness only. All generation ends before held-out scoring. Utility success is the predeclared 1% aggregate improvement / 5% family-regression screen.

## Paired differences (sparse on minus off)

- `utility_success_rate`: `0.0`
- `coverage`: `0.0`
- `selected_test_bins`: `0`
- `selected_test_fitness`: `0.0`

Only complete, usage-accounted pairs contribute to these means; failed pairs remain in the table and raw files. Fewer selected test bins is better; higher fitness is better.

## Interpretation limits

This is a descriptive pilot. No p-value, statistical equivalence, or general discovery advantage is asserted. Exact reference matches are known; other novelty labels are unresolved. NSR and distinct verified mechanism yield are unavailable. More diverse probe behavior or different syntax does not establish a novel algorithm.

Reproduce this report with `openend report RUN --output REPORT.md`. Recompute the saved evaluations with `openend replay RUN`; this makes no model calls.
