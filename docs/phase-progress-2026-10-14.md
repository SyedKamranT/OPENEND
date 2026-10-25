> **2026-10-25:** Native execution deferred by owner. Phase 4 remains open; [fixed-parent diagnostic](parent-opportunity-v1-results.md) completed 512 attempts without a new improvement. [Current work order](feedback-action-plan-2026-10-25.md).

> **Active order, 2026-10-15:** Phases 1–3 CLOSED → Phase 4 baseline implementation/protocol preparation (active). Existing baseline work is preserved. [Phase 3 closure](phase3-closure-v1.md). Large comparative experiments require prospective signal justification; confirmation remains Phase 13. This order supersedes historical next-step notes below.

# Phase progress — updated 2026-10-16

Current: [Phase 4 acceptance](phase4-acceptance-v1.md) and [native setup](native-environment-setup-v1.md).
Docker installed; firmware virtualization disabled, requiring BIOS change/restart.
Native prompt builders tested; containment probes pending. 147 tests pass, one optional skip.


Latest: [Decision counterexamples](phase4-decision-v1-results.md): 11,394 completions,
5,856 verified certificates, 1471 hindsight bins; useful online signal remains unestablished.
143 tests pass; Ruff clean. Phase 4 remains open.


Earlier: [Phase 4 signal diagnosis and parser correction](phase4-signal-v1-results.md).
84 online candidates found no useful witness; certified offline packings expose headroom.
141 tests pass, Ruff clean, 880 attempts replayed. Phase 4 remains active.


Current: [Phase 3 benchmark closure](phase3-closure-v1.md) accepted, including 816 reference
comparisons, five host cases, three stress panels and seven fixed-policy checks.
Useful improvement remains unestablished. Full suite: 133 passed; Ruff clean; 880 saved
attempts replayed exactly. Phase 4 implementation/protocol preparation is active.

**Phase 1 CLOSED:** [research lock v1](research-lock-v1.md) accepts the internal review by
owner instruction and removes external review as a progression requirement. Current work
is Phase 2–4 development; Phase 13 owns final inference and fresh-data confirmation.
The dated result summaries below retain their historical test counts.

Newest (2026-10-15): [baseline evaluator fidelity v3](baseline-fidelity-v3.md) establishes
concrete native/OPENEND action-space and aggregation differences with fifteen fixtures.
Historical next-step note: the adapted-baseline protocol now follows Phase 3 closure. Native fidelity remains incomplete.

Earlier: [eight development blocks](development-blocks-v1-results.md) completed 640 offline
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
| 2 Literature/gap | Closed: targeted internal review, 15 method records, claims/comparators adjudicated | Ongoing literature maintenance; no external approval pending |
| 3 Benchmark | Closed: contract, acceptance, sensitivity and signal diagnostics frozen | No construction blocker; useful signal remains unestablished |
| 4 Baselines | Active implementation/protocol preparation; existing adapters preserved | Native fidelity/containment, matched budgets and prospective signal justification before large comparison |
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
