# Utility study v1: design draft

> **Current status — 2026-10-15:** Phase 1 is closed under [research lock v1](research-lock-v1.md). This remains a later-phase experimental-design draft; its unresolved final inference decisions are owned by Phase 13 and do not reopen Phase 1.

2026-10-14. **Development design, not a frozen confirmatory protocol.** This separately
scoped study does not replace H4's independently validated discovery-yield hypothesis.

## Question and intervention

Does reference-distance parent weighting improve the packing utility of training-selected
policies over uniform parent selection, with shared resource allowances?

Both arms use the same model/digest, float evaluator, bounded JSON grammar, references,
probe panel, archive, replacement rule, prompts, training data and call/token ceilings.
Only parent sampling weights differ; prompt contents may differ because parents differ.
This is reference-distance weighting, not dynamic density estimation. Omit critic,
explicit target generation and retrieval symmetrically from this primary contrast.
Independent generation, grammar search and EoH/FunSearch adaptations are additional
development comparators; native reproduction remains a separate fidelity workstream.

## Outcome, selection and replication

For independent benchmark block b and paired search run r, define
`D_br = bins_uniform,br - bins_weighted,br`. Positive differences favor weighting.
Use equal numbers and lengths of streams in each of the four declared families, total
bins within a block, mean paired difference over runs within each block, then equal
weight over blocks. The target is mean benefit over the declared benchmark generator
and search randomness, conditional on the fixed model and domain.

Training and evaluation streams are separate within blocks. Each paired run shares data
across arms. Repeated search seeds on one block do not create independent task blocks.
Candidates, placements and streams are not independent search replicates. Uncertainty
must respect the shared block structure.

Select the valid generated policy with lowest training total bins, breaking ties by
earliest attempt. Use the best aggregate training reference unless a generated policy
strictly improves it; reference ties follow frozen reference order. Report generated-best
performance and fallback frequency separately. This is a prospective rule, not a relabeling
of historical fitness-selected runs. Verify objective consistency in archive, runner and
selection before implementation/freeze.

Keep the existing 1% reference improvement and 5% family-regression screens for development.
They are not significance criteria. A confirmatory between-arm practical margin and the
inferential treatment of family constraints still require justification.

## Failure and resource accounting

Record started requests before dispatch and every response, invalid output, duplicate,
truncation and terminal failure. Shared ceilings are not equal measured consumption;
report known tokens, unknown usage, runtime and evaluation work. Invalid proposals count
against allowance and can still lead to a valid completed-run fallback outcome.

Interrupted runs with unknown cost are not automatically completed fallback outcomes.
The planning summarizer refuses incomplete pairs. Freeze a replacement policy and
differential-failure sensitivity analysis before new inference; do not silently drop
failures. The interrupted adapter trial stays preserved. A replacement trial needs a new
prospective amendment and symmetric arms in a new directory, not a replayed model request
inserted into the old journal. This draft launches no inference.

## Synthetic analysis development

`openend.utility_planning` calculates block means and their standard error, with a
diagnostic normal-approximation interval. It rejects duplicate, incomplete, nonfinite and
unbalanced input; one block or constant block means do not yield an inferential interval.
This normal interval is **not the chosen final method**. Simulated coverage is measured.

The sensitivity grid uses 8/16/32/64 blocks, 1/4 runs per block and 1,000 studies per
scenario. Illustrative block/run standard deviations are each two bins per fixed suite.
Scenarios: null; one-bin effect; two-bin effect; two-bin effect mixed with 75% zero
differences; two-bin effect with independent 1% pair failure. The zero mixture's expected
effect is 0.5 bins. The illustrative one-bin practical margin is not a replacement for
the 1% screen. These continuous synthetic differences are not packing instances or
pilot-fitted estimates. Shared seeds aid reproducibility, not independent evidence.

Report conditional coverage and Monte Carlo error, widths, degeneracy and missing studies.
Fractions with lower bounds above zero/margin use *all* simulated studies as denominator;
coverage uses complete nondegenerate studies. No sample size is selected from this grid.
Extend to heavy tails, variance uncertainty, family heterogeneity, dependent failures and
realistic fallback behavior. Calibrate the final interval before reporting power, and
derive plausible variability from development evidence rather than the fresh holdout.

## Required before confirmation

Latest implementation update: the [training-only runner](utility-runner-v1-results.md)
now integrates total-bin archive/prompt/selection logic and replays an entire offline
engineering trial. It does not yet supply independent benchmark blocks or a live-model
confirmation protocol. The earlier development note below records the preceding stage.

Development update (2026-10-14): [objective and interval results](utility-development-v2-results.md)
now demonstrate an actual ranking reversal and provide a tested bin-count state component.
Student-t planning improves Gaussian coverage but leaves mixture concerns. Neither a live
utility runner nor a final inferential method is complete; the checklist below still applies.

Freeze and hash model/prompt/evaluator/grammar/probe versions; consistent objectives and
selection rules; benchmark generator and block sizes; blocks/runs and precision/power
justification; practical margins and analysis; resource ceilings and randomized execution
order; failure/replacement rules; one primary contrast and multiplicity treatment; and
holdout custody/access. Complete and hash training-selected policies before final evaluation.

No fresh holdout is generated here. External review is deferred for development. Changes
informed by final outcomes cannot retrospectively become preregistered decisions.
