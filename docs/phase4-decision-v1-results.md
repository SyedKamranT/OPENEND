# Phase 4 online decision diagnosis — 2026-10-16

Executed the [predeclared bounded protocol](phase4-decision-v1-protocol.md) on all 48
training streams. Enumerated 11,394 legal forced-action completions over 5,760 states
in two passes. No model calls, new policy search or evaluation/holdout access.

| Measure | Result |
|---|---:|
| Best Fit training bins | 1476 |
| Best single deviation per stream, summed | 1471 |
| Sequential hindsight rollout bins | 1471 |
| Required total for unchanged 1% screen | 1461 |
| Strictly improvable states on Best Fit paths | 8 |
| Distinct affected streams | 5 |

The hindsight rollout's family totals are uniform 402, bimodal 405, paired 401 and
triplets 263. It fails the aggregate utility screen. The eight state opportunities
must not be added: four occur in the same stream. The single-deviation aggregate
selects a separate hindsight action for each stream; it is not an eligible online policy.

## Concrete counterexamples

Steps are zero-based. Capacities are integer remaining space before placing the item.
Every alternative keeps the original prefix and uses Best Fit for the remaining suffix.

| Stream | Step | Item | Selected capacity → alternative capacity | Final bins |
|---|---:|---:|---|---|
| train/uniform/005 | 25 | 27 | 38 → 57 | 32 → 31 |
| train/bimodal/001 | 4 | 20 | 24 → 31 | 35 → 34 |
| train/paired/001 | 13 | 27 | 28 → 37 | 35 → 34 |
| train/paired/001 | 18 | 37 | 37 → 60 | 35 → 34 |
| train/paired/001 | 20 | 21 | 22 → 60 | 35 → 34 |
| train/paired/001 | 21 | 28 | 36 → 60 | 35 → 34 |
| train/paired/002 | 16 | 20 | 25 → 40 | 35 → 34 |
| train/paired/003 | 15 | 26 | 34 → 56 | 34 → 33 |

At paired/001 step 18, Best Fit takes a remaining capacity of 37 for an item of 37.
Choosing capacity 60 instead yields one fewer final bin under the fixed continuation.
Exact fit is therefore not universally optimal for the entire known future stream.
This example does not establish that avoiding exact fits improves an online policy.

## Interpretation and next implementation decision

This diagnostic isolates decisions allowed by the current host; unlike decreasing-order
offline packers, it preserves arrival order and the no-optional-opening constraint.
It still uses future information to choose actions, and is ineligible for deployment.
Best Fit completion is a restricted heuristic oracle, not optimal search: absent gains
do not imply there is no better multistep plan. The 6.1% offline headroom and 0.34%
restricted rollout gain measure different feasible sets and cannot establish an online
lower bound or impossibility result.

There is no evidence yet to promote a new representation or a useful-success claim.
Preserve these state/action counterexamples as training diagnostic fixtures. Next,
a separately bounded multistep completion diagnostic can test whether coordinated
choices matter; baseline score-temperature fidelity can proceed independently.
Do not add future-item features to candidate inputs or retune the 1% success screen.
Phase 4 remains open; Phases 1–3 closure is unchanged.

Artifacts: `results/raw/phase4-decision-v1` preserves the source archive, prospective
protocol, all action values, 48 input streams, both trajectories and hash manifest.
Independent verification checked 5,856 full packing certificates, all executed host
actions and all saved prefix/state correspondences.

Validation: **143 tests passed in 20.45s; Ruff clean.** Exhaustive 256 tiny-stream tests verify prefix preservation, certificate validity, baseline agreement and non-worsening hindsight rollout. No model calls.
