# OPENEND hypotheses and analysis status

**Status: PROVISIONAL; supersedes the previous locked hypothesis tests (2026-10-08).**

## H1 ? Exploration (pilot diagnostic)

Sparse-weighted parent selection changes behavioral coverage and the distribution of reference-relative distances compared with uniform parent selection. A gain in the optimized proxy alone is not evidence of useful invention. Report paired seed-level coverage and candidate-validity differences; investigate sensitivity with independent probes before confirmation.

## H2 ? Quality/diversity tradeoff (exploratory)

Sparse targeting improves held-out utility or coverage without a practically meaningful utility loss. The implemented comparison holds QD fixed. A QD-on/off factorial and normalized novelty?utility frontier are future studies; no current result isolates QD itself.

## H3 ? Verifier reliability (deferred)

An evidence-grounded verifier reduces false novelty claims at a prespecified recall/coverage requirement compared with a single model judge. Use one independently labeled pool, paired judgments, valid evidence links, source-idea clustering, abstentions, and both types of error. The fraction of naive claims debunked is not sufficient: it depends on prevalence and can reward rejecting everything. Calibration thresholds and sample size remain pending.

## H4 ? Distinct validated discovery yield (eventual primary hypothesis)

Let Y be distinct independently verified corpus-novel and utility-successful mechanisms per fixed resource allowance. The primary contrast is Delta = E[Y_sparse_on - Y_sparse_off] with all shared components held fixed. The statistical null for superiority is Delta <= 0; practical benefit additionally needs a prespecified meaningful margin.

The current screen cannot supply Y because a literature-based equivalence audit is absent. NSR and distinct discovery yield must remain unknown, not be imputed from distance or syntax novelty. Human-readable output and machine JSON explicitly reflect this limitation.

## H5 ? Expert evaluation (deferred)

Blinded experts prefer treatment outputs for meaningful originality/surprise while feasibility meets a prespecified noninferiority criterion. Freeze recruitment, compensation, consent, candidate selection, equal selection budgets, randomization, rating rubric, sample size, and appropriate ethics review before recruitment. Model task/candidate/rater dependence. Define the feasibility estimand and margin on a compatible scale; do not equate ordinal-logit coefficients with raw rating points.

## Analysis rules

The current run reports each paired seed and mean paired differences, without p-values or a confirmatory confidence interval. Seeds replicate search on one fixed benchmark; they do not establish generalization over independent task families. Candidates within a run are dependent and must not be pooled as independent observations.

Confirmatory work will select the primary contrast, meaningful effect margin, independent sampling unit, precision/power target, resampling hierarchy, and multiplicity family before final outcomes are inspected. Use paired task/run inference consistent with that design. Use a defined equivalence procedure to claim equivalence. Lack of significance or a confidence interval crossing zero is potentially inconclusive, not automatic falsification. See the [ASA statement](https://doi.org/10.1080/00031305.2016.1154108).

All negative, failed, and inconclusive runs remain in the record. An implementation/evaluator defect causes an explicit versioned amendment and rerun of affected comparisons, preserving previous artifacts.
