# Phase 1 closure audit — 2026-10-15

**Status: CLOSED.** Accepted review: [internal technical review, 2026-10-14](internal-technical-review-2026-10-14.md).
Authority: the project owner's explicit instruction to close Phase 1 using that review and
remove external review as a prerequisite. [Research lock v1](research-lock-v1.md) records
the amended scope and decisions. This is an explicit scope amendment, not a claim that
outstanding scientific evidence has been obtained.

## Closure checklist

| Canonical Phase 1 deliverable | Frozen decision/evidence | Status |
|---|---|---|
| Research question | Matched fixed-reference weighting versus uniform parent selection | Closed |
| Four to six hypotheses | Five hypotheses with development, deferred and inactive scopes | Closed |
| Operational novelty definition | Corpus-relative source/equivalence evidence; unresolved and internal labels retained | Closed |
| First domain | Capacity-100 online integer bin packing with bounded JSON policies | Closed |
| Evaluation metrics | Total bins, paired block estimand, family outcomes, coverage, validity and resources | Closed |
| Baselines | Classical references and named search/adaptation comparators; fidelity requirements assigned to Phase 4 | Closed |
| Experimental protocol | Training-only selection, matched allowances, saved selections before evaluation, prospective run configurations | Closed |
| Leakage rules | Existing data designated development; separate final protocol and fresh data required | Closed |
| Success/failure criteria | Strict training gain/fallback; practical development screens; full failure accounting; no equivalence from zeros | Closed |

The complete definitions and handoff are in [research lock v1](research-lock-v1.md).
The previous [open audit](phase1-closure-audit.pre-lock-2026-10-15.md) is preserved unchanged.

## Accepted evidence and limits

The internal review is accepted for design decisions. The external Gemini model audit is
preserved as a model audit; neither it nor this closure is relabeled an independent expert
review. No further external review is required to advance the project.

Existing engineering evidence includes 240-attempt utility replay, 640-attempt development
block replay, and pinned upstream baseline state fixtures. The last recorded implementation
verification was 123 tests passing with Ruff clean. This documentation closure does not
claim a new test run, a successful live comparison, independent novelty, or superiority.

## Work transferred to later phases

- Phase 2: primary-source mechanism coverage and internally reviewed claim/source matrix.
- Phase 3: benchmark numerical semantics and data/access contract hardening.
- Phase 4: native evaluator, prompt and probability fidelity; accounted model-backed baseline comparison.
- Phase 6: retrieval abstention and auditable mechanism/equivalence checks.
- Phases 10–11: prospective representation, controllability and critic diagnostics.
- Phase 12: optional and inactive human study.
- Phase 13: final sample size, margins, inference calibration and fresh-data protocol before outcomes.

Immediate next work is the native baseline evaluator/prompt audit identified in
[baseline fidelity v2](baseline-fidelity-v2.md). Later-phase failures do not retrospectively
invalidate the completed design phase; changes to frozen decisions require dated amendments.
