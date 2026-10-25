# Phase 3 sensitivity and useful-signal diagnostics — 2026-10-15

Executed the [prospective protocol](phase3-diagnostics-v1-protocol.md) with seven fixed
policies, three seeded stress panels and the reused training suite. No model calls,
new search, validation/test evaluation or confirmatory inference.

## Probe sensitivity

| Panel | States | First Fit / exact_fit disagreement | Policies changing archive cell versus legacy |
|---|---:|---:|---:|
| Legacy | 32 | 0 | — |
| Seed 2026101501 | 96 | 21.875% | 7/7 |
| Seed 2026101502 | 96 | 26.042% | 6/7 |
| Seed 2026101503 | 96 | 25.000% | 7/7 |

Stress panels deliberately include exact fits and mixed feasibility. They are not samples
from a claimed deployment-state distribution. Cell changes show descriptor dependence on
the panel; they do not establish that one panel yields a better search algorithm.
First Fit and exact_fit no longer collide, but the historical witness and its algebraic
rewrite still collide on every panel despite differing in training bin totals. A larger
probe panel therefore does not certify policy equivalence either. Keep the fixed search
panel and report these limitations; a replacement requires a prospective version change.

## Useful-signal assessment

| Fixed policy | Training bins | Passes 1% / family screen |
|---|---:|---|
| First Fit | 1493 | No |
| Best Fit | 1476 | No |
| Worst Fit | 1567 | No |
| exact_fit | 1487 | No |
| index | 1539 | No |
| Historical witness | 1475 | No |
| Historical algebraic rewrite | 1476 | No |

The aggregate threshold is 1461 bins: at least 15 fewer than Best Fit. The historical
witness remains 14 bins above that threshold. Its one-bin gain reproduces, but it cannot
justify a study powered for a useful effect. None of these seven candidates passes; this
is not exhaustive grammar search and does not demonstrate impossibility.

Decision: the benchmark is executable and its limitations measurable. Accept it as a
bounded development benchmark. Do not launch a large superiority experiment on this
basis. Phase 4 may prepare faithful controls and a bounded prospective signal diagnostic;
a final study needs credible effect-size/signal justification and fresh data in Phase 13.
Any representation extension must preserve old results and use a new protocol/version.

Artifacts: `results/raw/benchmark-diagnostics-v1` contains policy definitions, panel
states/signatures/hashes, descriptors, collision groups, all pairwise disagreements,
48 training streams and per-stream scores, source/protocol snapshots and manifest hashes.
