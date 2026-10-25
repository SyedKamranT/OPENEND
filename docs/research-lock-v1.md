# OPENEND Phase 1 research lock v1

**Status: CLOSED — internally reviewed development specification.**
Decision date: 2026-10-15. Authority: the project owner's explicit instruction to close
Phase 1 using the completed internal review and remove external review as a prerequisite.

This document supersedes the Phase 1 closure conditions introduced on 2026-10-08 through
2026-10-14. It returns Phase 1 to the canonical roadmap's purpose: selecting the question,
hypotheses, definitions, domain, metrics, baselines, protocol and decision rules. Literature
validation, baseline implementation, empirical confirmation and publication are subsequent
work, not prerequisites that indefinitely reopen this design phase.

The [internal technical review](internal-technical-review-2026-10-14.md) is accepted as the
design review. It remains a self-review by the implementation agent. No external review
is required to proceed. This decision does not change past results, fabricate independent
labels, or convert model judgments into expert validation.

## Locked decisions

| Item | Decision |
|---|---|
| Immediate research question | Does reference-distance parent weighting improve training-selected policy utility over uniform parent selection at matched allowances? |
| Broader research objective | Investigate whether the system can discover useful, distinct mechanisms relative to documented prior art; claims must match the evidence actually collected |
| First domain | Online one-dimensional integer bin packing, capacity 100, four documented synthetic families |
| Representation | Bounded JSON expressions and host-controlled feasible-bin placement; no arbitrary generated Python in the current experimental track |
| Numerical semantics | Existing float interpreter, protected division and clipping; exact-rational audits are sensitivity checks, not silent replacements |
| Intervention | Fixed-reference behavioral-distance weighting of parent selection; uniform arm differs only in sampling weights |
| Shared machinery | Same grammar, model/digest, data, probes, archive, replacement rule, selection, stopping and allowances within a controlled contrast |
| Primary development endpoint | Total bins used by the training-selected policy on separately generated development evaluation streams |
| Direction and aggregation | Uniform minus weighted total bins; average paired runs within each independently seeded block, then equal-weight blocks |
| Selection | Lowest training total bins, earliest generated tie; best training reference fallback unless a generated policy strictly improves it |
| Other components | Critic, retrieval and explicit target generation excluded symmetrically from the primary mechanism comparison; evaluated separately |
| Reference baselines | First Fit, Best Fit and Worst Fit using independent reference implementations |
| Search comparators | Uniform parent search, independent generation, random/tree mutation, and explicitly labeled EoH/FunSearch JSON adaptations |
| Native comparator track | Native EoH/FunSearch reproduction remains Phase 4 work; no claim of native fidelity for JSON adaptations |
| Novelty status | Known-reference/equivalent when supported; otherwise unresolved until a documented source/equivalence audit supports a scoped finding |
| Internal audit label | Any author/model-produced absence finding is internally assessed, corpus-relative and scope-limited; never labeled independently verified |
| Practical development screen | At least 1% fewer total bins than the best aggregate reference, with no family more than 5% worse than that reference |
| Uncertainty reporting now | Raw paired outcomes, block summaries and explicit degeneracy; no confirmatory p-values or equivalence claims |
| Failure sensitivity | Preserve all attempts and planned pairs; feasible-packing missing-outcome bounds are descriptive identification bounds, not confidence intervals |
| Development data | All old splits and public development blocks remain development evidence; never relabel them as fresh confirmation |
| External review | Removed as a Phase 1/project progression requirement; independent-review claims remain unavailable without actual independent evidence |

## Hypotheses and claim boundaries

H1 tests whether reference-distance weighting changes exploration behavior. H2 studies
utility/diversity tradeoffs; the immediate utility contrast operationalizes this part of
the program. H3 concerns verifier reliability and needs a labeled evaluation protocol.
H4's original independently validated discovery-yield claim is retained as an untested
aspiration, not a condition for progressing. H5's human preference study is optional and
inactive unless the owner later requests it. No H3/H4/H5 result is asserted by accepting
the internal review. Internally assessed discovery counts, if later introduced, must be
named separately and cannot be reported as the original independently verified H4 outcome.

Existing hypothesis text is retained as historical scientific intent where it is stronger
than this active scope. Distance, syntax uniqueness and archive occupancy are diagnostics,
not novelty certificates. No positive novel-success label is created by this lock.

## Execution protocol and resource decisions

The active executable development foundation is `utility_runner.py` plus `block_runner.py`.
The completed block protocol fixes eight public blocks, two paired search seeds and twenty
attempts per arm: 640 offline attempts. Its purpose is engineering/failure diagnosis, not
a powered superiority experiment. The model-backed baseline protocol will be a separate
prospective Phase 4 artifact; local-only inference remains the authorized execution mode.
Do not revive Azure or download models as a consequence of this closure.

No automatic run extensions, silent retries, outcome-selected budgets or omitted failures.
Record actual known usage and unknown usage separately. Interruptions are retained, and
replacement studies receive a new protocol and directory. Shared ceilings are not a claim
of equal realized compute. Save inputs, source, requests/responses, state, selection and
evaluation with hashes and offline replay. Freeze selections before evaluation.

The 1%/5% screens are the fixed development decision criteria, not a powered between-arm
margin. Confirmatory sample size, calibrated interval, multiplicity and between-arm
practical margin are explicitly **Phase 13 entry conditions**, to be set before final
outcomes are observed. No arbitrary seed count is declared adequately powered to close
this phase. Current normal/Student simulations and missing-outcome bounds are planning
tools; their limitations stay recorded.

## Leakage, success and failure rules

Generators see only training inputs/feedback. Search/selection finishes before evaluation;
evaluation results cannot modify selected candidates or extend that study. Final confirmation
requires a separately frozen protocol and a fresh access-controlled dataset after development
decisions settle. Local hashes provide provenance, not proof of external custody or zero
model-memory contamination. Source code may remain private; resulting review/reproduction
limitations must be stated.

Engineering success means the contract is executed, complete attempts are accounted,
certificates verify and saved decisions replay. Scientific success requires evidence for
the particular named claim and its practical margin. A negative result is retained; zero
observed differences or nonsignificance are not equivalence. Incomplete comparisons and
unresolved novelty remain explicitly incomplete/unresolved.

## Phase handoff

| Subsequent phase | Work owned by that phase |
|---|---|
| 2 Literature/gap validation | Expand mechanism-level primary sources, inspect native evaluator assumptions, maintain claim/source matrix and internal evidence review |
| 3 Benchmark hardening | Preserve float semantics, certificates and development-block separation; version any richer representation |
| 4 Baseline implementation | Complete prompt/evaluator/probability fidelity, containment for native code, and prospective model-backed comparison protocol |
| 6 Novelty system | Implement auditable source/equivalence checks and calibrated retrieval/abstention, with honest internal-review provenance |
| 10–11 Ablation/red-team | Separate proposal quality, representation limits and search effects using bounded prospective diagnostics |
| 12 Human study | Optional/inactive; no recruitment or approval required for current progression |
| 13 Final experiments | Justify sample size/margins, calibrate inference/failure policy, freeze exact methods and fresh-data access before outcomes |
| 14–18 Evidence/paper/reproduction/publication | Report only supported claims, preserve deviations and disclose code-access limitations |

Changes to these decisions require a dated amendment before new affected experiments.
Later negative results do not reopen Phase 1 by themselves. They inform the later-phase
decisions above. Phase 1 is complete under this expressly revised scope; external review
is not a pending approval task.
