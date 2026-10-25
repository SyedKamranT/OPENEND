# Phase 2 closure — literature and gap assessment

> Internal technical review completed: [review and corrections](phase2-technical-review-2026-10-15.md). Active register is [v3](../data/literature/phase2-evidence-v3.json): 14 selected-method reviews plus one README-only lead. Original v2 closure snapshot remains unchanged.

**Status: CLOSED, 2026-10-15.** Review type: internal source-based technical assessment,
accepted under the owner's internal-review requirement. Phase 3 is now active. Existing
baseline implementation and audits are retained for use after benchmark closure.

## Deliverables and acceptance

| Deliverable | Evidence | Decision |
|---|---|---|
| Closest-method coverage | [15-record evidence register](../data/literature/phase2-evidence-v2.json) | Complete for the bounded research question |
| Mechanism comparisons | [Method matrix](phase2-method-matrix-v2.md), with selection, retention, descriptors, evaluation and resource fields | Complete; unknown fields explicitly constrain claims |
| Primary-source/version provenance | URLs, versions and inspected sections; pinned EoH/FunSearch code manifests | Complete at stated paper/source-review level; not a replication certificate |
| Citation follow-up | [Search ledger](../data/literature/phase2-search-log-v2.json), MEoH/LMX/DGM chains and later-method searches | Complete targeted pass; not exhaustive citation coverage |
| Gap adjudication | Claim decisions below | Complete; broad originality claims rejected |
| Comparator obligations | Required controls and claim-dependent comparisons below | Frozen for subsequent design |
| Benchmark implications | Phase 3 handoff below | Ready |

This closes a targeted mechanism review, not a systematic literature review of all AI
science. The boundary is documented retrospectively. It includes selected method sections
and relevant algorithm appendices; it does not assert every page or every implementation
was audited. The existing broader literature map remains context. No unsupported negative
claim about adjacent systems is needed for the retained research question.

## Internal adjudication of the gap

| Proposed claim | Verdict | Basis / permitted wording |
|---|---|---|
| Combining LLM variation and QD is new | Reject | ELM, LMX and In-context QD establish overlap |
| Explicitly targeting unfilled regions is new | Reject | In-context QD and ACES establish related targeting mechanisms |
| Behavioral diversity in heuristic search is new | Reject | BehaveSim is a close comparison |
| Novelty-weighted parent selection is new | Reject as a broad claim | MEoH, ShinkaEvolve and DGM require mechanism-level distinctions |
| Our fixed-reference rule has no prior equivalent | Unresolved; do not claim | Targeted searches cannot certify absence across the literature |
| The matched fixed-reference-versus-uniform contrast is worth testing | Retain | It isolates a measurable design choice in the frozen bounded task setting |
| OPENEND has demonstrated superiority or novel discovery | Unsupported | Literature review and offline plumbing do not provide that evidence |
| A reproducible negative or positive bounded comparison can be useful | Retain as research rationale | Results must be reported with scope, failures, costs and limitations |

The project proceeds as a controlled empirical study. The potential contribution is the
resulting evidence about a particular search choice and its failure modes. Publication
value and methodological originality remain unproven; closing this phase does not promise
acceptance or a positive outcome. Do not replace that uncertainty with an architectural
novelty slogan.

## Comparator obligations

The primary contrast remains the Phase 1 lock: weighted versus uniform parent selection
with shared representation, archive, model and evaluator. Required supporting controls
are classical packing references, independent generation, simple incumbent search/tree
mutation, and clearly labeled EoH/FunSearch adaptations with comparable allowances.

Before claiming superiority of the selection mechanism beyond this contrast, include a
usage-aware selection control motivated by ShinkaEvolve/DGM and a behavioral-diversity
control informed by BehaveSim, or limit the claim to the tested uniform contrast. Implementing
these controls is Phase 4/10 work; paper-method names must not be attached to unfaithful ports.
MEoH is required in the comparison rationale, but its multiobjective setting is not silently
added to the frozen single-objective experiment. Explicit target generation, if reintroduced,
requires comparison with In-context QD/ACES-style mechanisms and controllability checks.

The EoH v3 paper describes five evolution operators including M3; the pinned v0.1 recipe
and existing adapter use a four-operator schedule. A future protocol must name which
recipe it implements. Existing evaluator eligibility, prompt and score-scale differences
remain documented in [baseline fidelity v3](baseline-fidelity-v3.md). No historical run is
reclassified or discarded.

## Phase 3 handoff and closure conditions

1. Freeze a benchmark contract with items/capacity, feasible-bin eligibility, opening rule,
   tie order, float/protected-division/clipping semantics and bounded representation.
2. Demonstrate independent packing certificates and reference agreement, and retain the
   native-evaluator counterexamples as scope checks.
3. Freeze training/evaluation access, dataset identity, selection-before-evaluation and
   source/data manifests. All inspected public sources and existing splits stay development.
4. Verify total-bin aggregation, family screens, fallback/selection ties, resource/failure
   accounting and the reporting contract. Coverage and distance are not novelty labels.
5. Separate fixed-reference distance, live density and target reachability; state which
   diagnostics the current benchmark supports and test probe sensitivity before broader claims.
6. Record executable acceptance evidence and unresolved limits. Only then begin the new
   Phase 4 comparison protocol; final inferential design remains Phase 13.

## Limitations accepted at closure

HSS-MEoH is a screened repository lead, not a fully audited comparator. AlphaEvolve's exact
sampling probabilities were not established. Several cross-paper token costs and additional
code versions remain unknown. These uncertainties prohibit corresponding claims, but do
not prevent testing the already defined primary contrast. Further literature maintenance
continues before manuscript submission; there is no external-review approval pending.
