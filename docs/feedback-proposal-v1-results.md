# Matched feedback pilot — 2026-10-25

Completed the [frozen 12-call protocol](feedback-proposal-v1-protocol.md) using the installed
local Qwen 3.5 4B model and its pinned digest. All responses completed, parsed under the
unchanged finite grammar, and satisfied the one-subtree revision bound. No retries,
repairs, model downloads, new evaluation data or native execution.

**No proposal improved its supplied parent. All selected policies fell back to the
parent. Adding harmful examples did not improve selected performance in this pilot.**
This does not establish that feedback is ineffective in general: there are only four
matched parent/seed opportunities per condition, one model and one prompt specification.

| Measure | No examples | Beneficial only | Beneficial + harmful |
|---|---:|---:|---:|
| Completed, eligible proposals | 4 | 4 | 4 |
| Accepted parent improvements | 0 | 0 | 0 |
| Exact parent copies | 0 | 0 | 0 |
| Raw candidates worse than parent | 3 | 4 | 3 |
| Reference training-trajectory matches | 3 | 3 | 3 |
| Actual input + output tokens | 2657 | 3020 | 3613 |
| Beat 1475 / pass 1% screen | 0 / 0 | 0 / 0 | 0 / 0 |

Equal call and token allowances are not equal realized token cost. Mixed adds two
harmful examples to the same two beneficial examples and therefore uses a longer
prompt. These results do not isolate label valence from additional prompt content.

## Complete-trajectory results

Numbers below are raw generated-policy total bins. Selection fell back to 1476 for
each BF parent and 1475 for each witness parent in every condition.

| Parent / seed | No examples | Beneficial only | Beneficial + harmful |
|---|---:|---:|---:|
| BF / 2026102601 | 1476 | 1567 | 1476 |
| BF / 2026102602 | 1545 | 1545 | 1545 |
| Witness / 2026102601 | 1476 | 1476 | 1476 |
| Witness / 2026102602 | 1476 | 1476 | 1476 |

At BF seed 2026102602 all three conditions reproduce the existing residual-preference
rule `-abs(gap-item)` (encoded with `1*item`), using 1545 bins. The no-example arm still
received the common intervention expression and scope warning. This is a feedback
ablation, not unprimed generation; possible anchoring is a limitation, not an established
causal explanation. The restrictive revision bound and model capacity are also potential
limits that this small experiment cannot distinguish.

Nine of twelve responses have identical assignments to a reference across all 48
training streams; one matches Worst Fit and eight match Best Fit. That is empirical
agreement, not a universal equivalence proof. All eligible policies were run from the
beginning of every stream, including states absent from BF trajectories. BF-prefix
intervention labels were computed only as secondary diagnostics, never as the selection
objective. The fallback is selection-time retention of the parent, not a runtime
conditional operator or a way to conceal the raw regressions.

## Decision and milestones

Do not promote mixed feedback, expand this run, or evaluate a selected procedure on new
data: no procedure earned promotion here. The completed runner now supports auditable
matched feedback tests, but its engineering success is not an algorithmic improvement.
Before further prompt tuning, prioritize the pending reviewed published nonlinear
controls as a separate prospective diagnostic of useful online headroom. Any subsequent
feedback experiment must address this pilot's common-example anchoring and restrictive
edit scope explicitly, with a new specification rather than a silent retry.

Milestones remain: beat 1475; reach at most 1461 with family constraints; freeze and
replicate on new development data; then test whether reference weighting adds benefit
over matched controls. Final confirmation remains untouched. No sparsity, novelty,
superiority, Phase 4 closure or independent-review claim follows from this result.

## Verification and artifacts

`results/raw/feedback-proposal-v1` preserves the pre-call request plan, config, protocol,
source archive, input hash, backend identity, all 12 started/response pairs, exact token
usage, scores, reference-distance panels, local intervention diagnostics and 576 complete
packing certificates. No unresolved starts or unknown usage remain. All 576 certificates,
their assignment digests and every host action were checked independently. Saved-response
replay recomputed every score and selection exactly without model calls; artifact hashes
matched. `verification.json` records the checks and aggregate outcomes.

Validation: **149 passed, 2 skipped in 58.99s; Ruff clean.** Optional NumPy/SciPy modules
remain unavailable in the restored environment; their earlier separate numerical audit
is unchanged. The protocol was frozen before calls; results were written afterward.

Reproduce against the captured source and inputs:
`python -m openend.feedback_proposal replay results/raw/feedback-proposal-v1`.
The verifier rejects source or input drift rather than silently replaying a changed runner.
