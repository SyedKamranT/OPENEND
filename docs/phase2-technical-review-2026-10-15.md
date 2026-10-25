# Phase 2 internal technical review — 2026-10-15

**Verdict: retain Phase 2 closure with the corrections below; proceed to Phase 3.**
This is an internal implementation-agent review, not an independent technical endorsement.
The original Phase 2 lock and historical evidence remain intact. The corrected active
[evidence register v3](../data/literature/phase2-evidence-v3.json) supersedes v2 for interpretation.

## Findings and fixes

| Finding | Why it matters | Resolution |
|---|---|---|
| The 15-record total obscured uneven review depth | A README screen is not equivalent to method inspection or replication | v3 labels 14 selected-primary-method reviews and one README-only lead; all carry explicit replication status |
| Four-operator EoH wording could suggest missing upstream capability | The pinned source implements M3 despite excluding it from the default list | Corrected: default activation versus source support; paper/default/adapter recipes must remain distinct |
| Fixed-reference distance could still be read as underexploration | Distance to three references does not measure density of the evolving archive or discovery novelty | Phase 3 contract gives the exact distance/weight formula and prohibits those interpretations |
| Probe agreement was too weak to support behavior equivalence | Existing probes never contain an exact fit or infeasible bin | Added executable exact-fit counterexample and probe-coverage report; kept historical probes unchanged |
| Matched uniform control alone cannot justify a broad selection-method claim | Different existing selection mechanisms may explain any gain | Preserve primary contrast; require usage-aware and behavioral-diversity comparisons for broader claims, plus a simple incumbent control |
| Experimental usefulness was not tied clearly enough to measurable signal | A technically correct run may be uninformative in a restrictive language | Require training-only representation/signal diagnostics before a large study; retain failures and distinguish 1% screening from between-arm inference |

The EoH correction follows pinned `getParas.py` (default operator list) and
`eoh_evolution.py` (`get_prompt_m3` and `m3`), under the existing source manifest.
It is a clarification of audited code, not a new model-based judgment about the paper.

## Concrete Phase 3 evidence

`results/raw/benchmark-acceptance-v1/report.json` records 816 comparisons between expression
references and separate imperative packing implementations: 768 tiny-stream checks and
48 checks across sixteen development streams. Five hand-specified host cases check opening,
feasibility filtering, exact fit, ties and restriction to opened bins.

All 32 legacy probes have all six bins feasible, no exact fits, and no opening decisions.
Constant-zero First Fit and the `exact_fit` policy have identical probe signatures.
For item 40 and residual capacities [80, 40], they choose bins 0 and 1 respectively.
This disproves using probe equality as general behavioral equivalence. It does not show
that the panel is useless for its narrow descriptor purpose.

Known reference policies can themselves have positive reference-distance scores. That is
expected for an average over the two nearest reference signatures and cannot be promoted
to a novelty certificate. The new regression checks preserve this distinction.

## Decisions that improve the research

Use an explicit benchmark contract before further model spending. Report held-out
within-family development performance separately from distribution-shift generalization.
Use diagnostic states for exact-fit/feasibility sensitivity, without tuning the primary
search panel on evaluation outcomes. Opening cases exercise the host, not archive descriptors,
which currently require at least one feasible existing bin.

A representation witness establishes expressibility only for its demonstrated gain and
inputs. The existing small training gain does not establish the 1% screen or statistical
power. Do not manufacture a positive witness, extend budgets after seeing results, or
label a synthetic fixture as discovery evidence. If useful gains remain unreachable or
unmeasurable, document a prospective representation/benchmark amendment before new trials.

The [Phase 3 contract](phase3-benchmark-contract-v1.md) now owns these requirements. Phase 2
remains closed for its limited, internally reviewed purpose; no originality or superiority
claim has become established through this review.

Validation this continuation: **130 tests passed in 41.60s; Ruff clean.** Evidence-level
counts, local links and diagnostic implementation hash verified. No new model calls.
