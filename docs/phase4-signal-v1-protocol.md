# Phase 4 training signal diagnostic v1

Prospective specification, 2026-10-15; written before execution.

Use only the existing 48-stream training suite. Preserve the evaluator, historical
search panel and 1% aggregate / 5% family screen. No model calls or evaluation splits.

Measure certified offline first-fit-decreasing and best-fit-decreasing assignments,
remapped into original item order and checked independently. These use future items:
they are diagnostic feasible upper bounds on offline optimum, not eligible policies,
not exact optima, and not evidence of online attainability. Record elementary lower
bounds and known planted optima separately.

Evaluate exactly 84 attempted online candidates: four templates at t=k/20 for
k=0..20, in template-major order. Templates are max(t-gap,0), -abs(gap-t),
exact_fit-gap-t*index, and -gap+t*index. Use the unchanged production interpreter.
Constants outside the proposal vocabulary are an explicitly expanded diagnostic
search space; report eligibility under the actual proposal parser separately.
Duplicates consume attempts and may reuse evaluation. Do not stop on a favorable
result. Rank eligible screen passers by total bins then attempt order; if none pass,
report the minimum-total candidate with its family-screen status. No retuning within
this version, no inference or novelty claim, and no new test-set access.

Preserve every candidate, score, chosen-policy certificate, offline certificate,
source snapshot and protocol hash. A useful training witness justifies a later
prospective development replication, not a superiority claim. A negative result
justifies representation/search diagnosis, not lowering the threshold.
