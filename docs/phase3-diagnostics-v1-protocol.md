# Phase 3 diagnostic protocol v1 — 2026-10-15

Written before this diagnostic execution. Public development checks only; no model calls.
Freeze seven policies: First/Best/Worst Fit, exact_fit, index, the previously discovered
threshold expression and its prior algebraic rewrite. No new policy search or tuning.

Compare the legacy panel with three independent seeded panels (2026101501–2026101503),
each containing 32 ordinary all-feasible, 32 exact-fit and 32 mixed-feasibility states.
Every state has six bins and at least one feasible bin. Shuffle bin order within the new
states. Opening is separately covered by host acceptance tests, not these descriptors.
Report panel hashes, signatures, pairwise disagreement, reference distances, descriptor
cells and collision groups. These are designed stress cases, not estimates of task-state
frequencies. Do not select a winning panel or replace the legacy search panel.

Re-evaluate the same seven policies on the existing 48-stream training suite only. Report
total/family bins and the unchanged 1%/5% utility screen. Compute the integer total-bin
threshold and shortfall. The first-improvement historical diagnostic was stopped early;
this fixed-policy check cannot estimate the best attainable solution or success frequency.

If no fixed candidate passes the useful-gain screen, mark useful signal unestablished.
Benchmark correctness can still be accepted, but a large superiority experiment is not
justified. Follow-up representation diagnostics require a separate prospective protocol.
Preserve inputs, implementation/dependency hashes and outputs in a new directory. Never
reuse validation/test data or alter saved outcomes. No confirmatory inference is performed.
