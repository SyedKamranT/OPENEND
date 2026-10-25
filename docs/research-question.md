# OPENEND research specification

**Status: CLOSED — Phase 1 development research lock, 2026-10-15.**
The project owner accepted the completed [internal technical review](internal-technical-review-2026-10-14.md)
and removed external review as a progression requirement. The authoritative decisions are
in [research lock v1](research-lock-v1.md). The [closure audit](phase1-closure-audit.md)
accounts for all nine roadmap requirements.

## Research question

Under matched model and resource allowances, does fixed-reference behavioral-distance
weighting of parent selection improve exploration or utility relative to uniform parent
selection in bounded online bin-packing policy search?

The broader objective remains discovering useful, distinct mechanisms. Reference distance,
archive occupancy and an internally assigned novelty label do not establish that objective.

## Locked specification

| Requirement | Decision |
|---|---|
| Question | The matched parent-selection contrast above |
| Hypotheses | H1 exploration and H2 utility are development questions; H3 verifier reliability is later work; H4 independent discovery yield remains untested; H5 human study is inactive |
| Novelty | Corpus-relative, source-supported mechanism assessment; unresolved cases remain unresolved; internal review is labeled internal |
| Domain | Online integer one-dimensional bin packing, capacity 100, four development families, bounded JSON policy expressions |
| Metrics | Primary development utility is total bins; report equal-weight paired block differences, family performance, validity, coverage and complete resource accounting |
| Baselines | First/Best/Worst Fit; uniform, independent generation, mutation, and explicitly labeled EoH/FunSearch adaptations; native fidelity belongs to Phase 4 |
| Protocol | Training-only search and selection, same allowances and evaluation inputs across arms, selections saved before evaluation; exact run settings frozen before each study |
| Leakage | Existing data are development data; final confirmation requires a separately frozen protocol and fresh controlled data |
| Success/failure | Replay and certificate checks establish engineering correctness; scientific claims require measured evidence; failures, negative results and unknown usage are retained |

[Research lock v1](research-lock-v1.md) specifies selection, practical screens, stopping,
missing-outcome handling and phase ownership. It controls if historical documents differ.
This closes design decisions; it does not mark later experiments or baseline fidelity complete.

The [pre-lock specification](research-question.pre-lock-2026-10-15.md) is retained for provenance.
Its superseded external-review closure conditions are inactive.
