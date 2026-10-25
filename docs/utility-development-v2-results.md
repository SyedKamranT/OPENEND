# Utility development: objective alignment and interval sensitivity

2026-10-14. Development evidence only; no new model calls or fresh holdout access.

## Objective audit

The historical runner maximizes mean per-instance lower-bound/bin-count fitness in archive
replacement, parent feedback and candidate selection. That is consistent with its original
protocol, but it is not identical to minimizing aggregate bins in the prospective utility
study. Changing only final selection would leave an internally mixed new objective.

`openend.objective_audit` verified the preserved deeper diagnostic's artifact hashes,
found an objective reversal, and recomputed both policies on the training suite:

| Saved proposal index | Total training bins | Ratio fitness |
|---|---:|---:|
| 705 | 1,490 | 0.9074151385030181 |
| 477 | 1,491 | 0.9074331574815447 |

The ratio objective prefers proposal 477 despite its extra bin. This is an objective
distinction, not evidence that the original implementation failed its own contract.
Full expressions and source-event hash are saved in `results/raw/objective-audit-v1/audit.json`.
This post-hoc check changes no policy and is not a new adaptive search.

Added `openend.utility_state.UtilityState` for the prospective total-bin study. It uses
negative total bins as archive quality, explicitly labels parent feedback with training
total bins, and uses the same total for final selection. It retains the first generated
tie and falls back to the first best reference unless a generated policy strictly improves.
Synthetic ranking-reversal tests deliberately supply conflicting fitness values; archive,
parent and winner still agree on total bins. Returned selections cannot mutate state.

**Integration status:** this state component is tested but is not yet connected to a live
budgeted runner. Historical `experiment.py`, prompt semantics and replay remain unchanged.
Do not launch the new study through the legacy runner and claim total-bin consistency.
The next runner must use this state, total-bin system prompts, accounting and full replay.
Do not interpret the underlying generic archive's negative quality sum as the historical
normalized QD score; the future report needs an explicitly named metric.

## Student-t planning comparison

The planning code now supports a separate Student-t mode with degrees of freedom equal
to independent block count minus one. It uses the published rounded 0.975 critical values
for 7, 15, 31 and 63 degrees of freedom. Other block counts are rejected explicitly.
The formula and values follow [NIST confidence limits for the mean](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm)
and [NIST's t table](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3672.htm).
Under independent normal block means this accounts for estimated variance; it does not
guarantee coverage for asymmetric mixtures, dependence or outcome-related failures.

Ran the same forty synthetic scenarios and seeds as v1, totaling 40,000 simulated studies.
Both source and result hashes verified. Four-run-per-block results are:

| Blocks | Gaussian null: normal coverage | Gaussian null: Student coverage | Mostly-zero mixture: Student coverage |
|---|---:|---:|---:|
| 8 | 90.8% | 95.7% | 93.0% |
| 16 | 92.0% | 94.6% | 93.6% |
| 32 | 95.4% | 96.6% | 92.8% |
| 64 | 95.5% | 95.7% | 94.4% |

Coverage is conditional on complete nondegenerate studies. The eight-block mostly-zero
scenario has 999 such studies; the other displayed cells have 1,000. Coverage Monte Carlo
standard errors are about 0.006–0.008 and are stored per scenario. Sampling fluctuation
is expected; this table is not evidence of monotonic coverage improvement with block count.
The Gaussian comparison uses identical underlying simulated data in the two modes.

The zero mixture is asymmetric when its component effect is positive. Student adjustment
helps the Gaussian case but has not resolved mixture undercoverage. Do not choose a
confirmatory sample size or claim empirically established power from these assumed scales.
Independent-failure assumptions and strict complete-study handling are unchanged; larger
studies remain vulnerable to incomplete pairs. A failure-aware design is still required.

Preserve `results/raw/utility-planning-v1` and `results/raw/utility-planning-student-v2`.
Run a reproducible new Student scenario grid into an unused directory with:

```powershell
.venv\Scripts\python.exe -m openend.utility_planning results/raw/<unused-directory> --interval student
```

The original normal summarizer remains available. Both modes flag constant block outcomes
instead of reporting spurious zero uncertainty. Tests confirm that duplicating identical
within-block runs does not increase the independent degrees of freedom.

## Next development gate

Implement the versioned utility runner with matched prompts, state, budget and replay;
first exercise it with scripted responses and offline mutation. Develop block resampling
or another justified interval with explicit treatment of degenerate/zero-heavy outcomes,
and test non-Gaussian and failure-dependent scenarios before selecting it. Complete the
baseline replacement protocol before further inference. External review stays deferred.
