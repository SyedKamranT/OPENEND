# Coordinated scoring diagnosis — 2026-10-25

Executed the [prospective finite census](coordinated-sketch-v1-protocol.md): 64 sketches,
five controls, 48 existing training streams. All attempts completed. This is adaptive
development using previously inspected data, not a replication or confirmation.

**The current generator can express a rule that makes a beneficial choice at all eight
saved counterexamples, but that rule fails badly when applied generally.** The tested
finer constants/deeper expressions do not produce a better complete online policy.

| Policy or family | Best total bins | Beneficial / harmful BF-state decisions |
|---|---:|---:|
| Residual-preference sketches (8) | 1512 | Varies by sketch |
| Plateau sketches (8) | 1476 | 0 / 0 for first best sketch |
| Triangular-adjustment sketches (48) | 1476 | Includes zero-weight BF ablations |
| Eligible residual rule `-abs(gap-item)` (encoded with `1*item`) | 1545 | 8 / 67 |
| First Fit control | 1493 | 4 / 19 |
| Best Fit control | 1476 | 0 / 0 |
| Worst Fit control | 1567 | 7 / 92 |
| Historical witness control | 1475 | 2 / 2 |
| Previously selected `max(gap,fraction)` control | 1476 | 0 / 0 |

Twelve of 64 sketches satisfy the current proposal grammar. All 64 satisfy the unchanged
production interpreter. The other 52 are explicitly diagnostic expressions outside the
proposal grammar; they were not silently added to generation. Zero sketches beat the
1475 incumbent; zero pass the unchanged 1461-bin aggregate and family-regression screen.
Every result includes the four reference-distance measurements; these are not estimates
of archive density or independently adjudicated novelty.

## Mechanistic interpretation

The eligible residual rule favors a remaining capacity near twice the arriving item.
It chooses beneficial alternatives on all eight previously identified states. However,
it also chooses harmful alternatives on 67 other BF states and makes 536 neutral
deviations. Its full trajectory uses 69 more bins than BF. That establishes local
action expressibility for these examples, not expressibility of a globally better policy.
The best all-eight-correcting sketch outside the generator uses 1540 bins (8 beneficial,
64 harmful decisions), which also fails.

The hindsight labels mean: force this action after the saved BF prefix, then complete
with BF. They do not predict the outcome of applying the rule repeatedly. Counts and
gains must not be added across states. The historical witness's 2 beneficial and 2
harmful decisions illustrate why complete trajectory evaluation remains necessary.

No evidence here proves a representation ceiling, online impossibility, or need for
cross-bin features. A blanket residual preference is demonstrably too indiscriminate.
Increasing distance weights does not address this observed failure mode.

## Decision and next work

Keep the production grammar and locked selection comparison unchanged. Before scaling
search, specify a selective revision mechanism that receives both verified beneficial
and harmful training examples and proposes bounded changes with an explicit BF fallback.
Its objective must remain complete packing performance; counterexample coverage alone
is an inadequate objective. Compare it with mutation and incumbent improvement at matched
cost, and separate any representation extension from proposal/selection changes.

Known published nonlinear scoring controls remain a separate pending work item. The five
controls here are reference/historical controls, not faithful EoH/FunSearch reproduction.
Such published controls need reviewed source-specific formulas, numerical/action
adaptations and a prospective budget. No claim about their potential performance is
made by this census. Native Phase 4 and fresh confirmation remain open.

The new external-chat feedback is advisory, not independent review. Its observation
that the earlier subtree arm repeats the parent-opportunity experiment is correct:
those reports are not independent replications. This census is also training development.

Artifacts: `results/raw/coordinated-sketch-v1` contains the pre-scoring candidate plan,
protocol, source archive, input hash, all scores, state-effect counts and opportunity
actions, and 3312 complete packing certificates. Exact replay matched every result;
all manifest hashes, assignment digests, certificates and host actions were verified.

Validation: **146 passed, 2 skipped in 27.00s; Ruff clean.** The two skips are optional
NumPy/SciPy audit modules absent from the restored environment. The earlier six numerical
audit tests passed separately in the bundled runtime; they were not rerun for this change.
