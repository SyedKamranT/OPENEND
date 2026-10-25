# Phase progress — updated 2026-10-15

**Phase 1 CLOSED:** [research lock v1](research-lock-v1.md) accepts the internal review by
owner instruction and removes external review as a progression requirement. Current work
is Phase 2–4 development; Phase 13 owns final inference and fresh-data confirmation.
The dated result summaries below retain their historical test counts.

Newest: [eight development blocks](development-blocks-v1-results.md) completed 640 offline
attempts with separate training/evaluation seed domains and saved selections before
evaluation. All eight block differences were zero; no equivalence claim. Missing-outcome
identification bounds are also implemented. Final inference and scientific evidence gates
remain open; the development data-plumbing gate is complete.

Newest: [the total-bin runner](utility-runner-v1-results.md) completed and replayed 240
offline attempts with no improvement; the intervention changed parents in 35/120 paired
positions. Integration is complete for training-only offline/scripted backends. Independent
development blocks and the live protocol remain next. Current suite: 115 tests pass.

Earlier development: [objective alignment and Student-t sensitivity](utility-development-v2-results.md).
The total-bin state component and its subsequent runner integration are tested.
The interval comparison improves Gaussian calibration without closing mixture/failure concerns.

Numbering follows `../phases.md`. Its original prose is historical intent. Later engineering
proceeds under the completed Phase 1 design lock; no overall percentage is warranted.

| Phase | Current state | Remaining acceptance condition |
|---|---|---|
| 1 Research lock | Closed 2026-10-15; internal review accepted | None; later-phase empirical work follows research lock v1 |
| 2 Literature/gap | Eleven frozen leads; development retrieval | Broader mechanism search and independently adjudicated labels |
| 3 Benchmark | Bounded evaluator, references, certificates and replay implemented | Final numerical/data/access contract |
| 4 Baselines | References, generation/mutation and JSON adapters; interrupted trial | Complete accounted comparison and native fidelity/containment |
| 5 OPENEND v0 | Prototypes exist; critic/target gates failed | Controlled evidence for the narrowly defined intervention |
| 6 Novelty system | Conservative labels, retrieval and review packet | Validated source-based decisions and abstention |
| 7 Evolutionary discovery | Mutation/recombination and adapter state machinery | Operator fidelity and comparative utility evidence |
| 8 QD archive | Finite behavioral archive implemented | Probe/descriptor sensitivity; occupancy is not novelty |
| 9 Novel-success metric | Accounting and unknown status defined | Independently validated novelty and utility labels |
| 10 Ablations | Sparse/control engineering trials exist | Prospective contrasts after component selection |
| 11 Red-team | Disguises, false predictions and numerical sensitivity checked | Broader frozen adversarial evaluation |
| 12 Human study | Optional/inactive, not conducted | Activate only if separately requested |
| 13 Final experiments | Not started | Frozen design and fresh controlled holdout |
| 14 Evidence freeze | Per-run snapshots exist | Comprehensive final evidence/deviation freeze |
| 15 Paper | Proposal/draft only | Results-led manuscript with supported claims |
| 16 Internal review | Current technical self-review complete | Later manuscript critique; independent review not implied |
| 17 Reproducibility audit | Local tests and replay exist | Clean-environment reproduction |
| 18 Publication | Not started | Mature contribution and venue decision |

## Work completed in this continuation

Added the [utility-study draft](utility-study-v1-draft.md), separating utility from H4,
and executable block-aware synthetic planning in `src/openend/utility_planning.py`.
Tests ensure repeated runs in one block do not artificially shrink block uncertainty,
missing pairs cannot disappear silently, zero variation is flagged, and simulations
reproduce from their seeds.

Saved `results/raw/utility-planning-v1` contains source, hashes and 40 scenarios totaling
40,000 simulated studies. It uses no model calls and no packing holdout. Scales are
illustrative, so these are design diagnostics, not empirical power or a chosen sample size.

For four runs per block, the nominal 95% normal interval covered the true null mean in
90.8% of 1,000 eight-block studies, 92.0% at sixteen blocks and 95.4% at thirty-two.
The mostly-zero scenario still covered only 91.9% at thirty-two blocks. This rules out
uncritically adopting the simple interval for the final analysis. Monte Carlo uncertainty
is included in the raw report.

Under independent 1% pair failure, 908/1,000 studies with 64 blocks and four runs had
at least one incomplete pair. This reflects the strict complete-study rule, not an
observed model failure rate. It demonstrates why failure/replacement policy must be
designed alongside sample size rather than handled by post-hoc deletion.

Next: calibrate a suitable small-sample/block interval, extend realistic sensitivity
assumptions and get development variance ranges; reconcile the implementation's fitness
objective with the proposed bin-count selection; then finalize the baseline replacement
protocol and fidelity fixtures. External review is deferred and does not block this work.
Historical failures and the fresh-holdout boundary remain intact.
