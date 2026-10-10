# Critic contract calibration: gate failed

Completed 2026-10-10 with local Qwen 3.5 4B. Six of six calls completed with accounted usage (2,527 tokens); all six responses contained valid executable revisions. No held-out data were accessed. The [prospective protocol](critic-calibration-v1-protocol.md) was unchanged during execution.

| Prompt condition | Valid responses | Correct reference classifications | Correct original choice vectors | Correct revision choice vectors | Training utility successes |
|---|---:|---:|---:|---:|---:|
| Minimal | 3/3 | 2/3 | 0/3 | 0/3 | 0/3 |
| Full scoring contract | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 |

Each choice vector contains three decisions; a vector is correct only when all three match. These are vector-level counts, not claims that every individual predicted choice was wrong. The predeclared full-contract acceptance gate failed. Two full-contract revisions and one minimal-prompt revision changed behavior on the fixed states, but none passed the training utility screen.

For `mul(gap, exact_fit)`, exact fits have zero gap and non-exact fits have zero exact-fit indicator. Thus every feasible bin scores zero and earliest-bin tie-breaking implements first-fit. The full-contract response classified it as best-fit and predicted `[1,2,1]` instead of `[0,0,0]`. Its unchanged revision was assigned another incorrect prediction, `[1,1,1]`. Schema constraints enforce shape; they did not enforce consistent algorithm reasoning.

This small diagnostic does not establish that a full contract generally hurts reasoning, that larger models fail similarly, or that useful search is impossible. The two arms share a new structured response format; it is not a direct replication of the old prose critic. It does establish that this model/prompt setting failed the necessary correctness check on these fixed cases. Adding missing instructions alone has not repaired the observed critic weakness.

## Consequence for the architecture

Do not promote schema-valid model critique into trusted verifier output or advertise the critic as calibrated. Generate revisions as proposals, obtain behavior traces and utility from deterministic tools, and pass only checked facts into subsequent search. Labels such as `other` cannot establish novelty. Keep the existing conservative equivalence checker and novelty abstention.

Next, implement an evidence-producing critic tool interface: the evaluator supplies actual scores, chosen bins and reference comparisons; model claims are checked and rejected or explicitly marked unsupported. Compare that tool-grounded role against proposal-only generation under shared budgets. A separate fixed target-controllability calibration still needs to test the descriptor instructions before another search-efficacy run. Expanded retrieval evaluation, stronger search baselines, fresh confirmation data and independent novelty assessment remain open.

Evidence: `results/raw/critic-contract-qwen35-4b-v1` contains source snapshot, frozen cases/requests/training data, pre-call journal, raw outputs, assessments and summary. **Seven artifact hashes verified; all six responses replayed with zero model calls.** The repository has **69 passing tests** and passes Ruff. Qwen was unloaded after completion. Phase 1 and the full goal remain open.
