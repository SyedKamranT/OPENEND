# Phase 2 mechanism and gap review — 2026-10-15

**Historical progress note. Superseded by [Phase 2 closure](phase2-closure-v1.md), 2026-10-15.** Internal source review is the accepted workflow.
Phase 1 remains closed. All Phase 3/4 implementations, source pins and audit results are
preserved; a new baseline experiment waits for the literature and benchmark decisions.

The [structured evidence register](../data/literature/phase2-mechanism-review-v1.json)
records three close methods, inspected sections, provenance, search queries, uncertainties
and citation leads. It is separate from the frozen candidate-novelty corpus: adding a paper
here does not silently change past retrieval scores or candidate judgments.

## Consequence for our contribution

The existing map omitted In-context QD and ACES. The register establishes relevant overlap
and upgrades BehaveSim from abstract-level awareness to selected-method inspection.

| Prior work | Source-backed overlap | Consequence |
|---|---|---|
| [In-context QD, v2](https://arxiv.org/html/2404.15794v2) | Archive-conditioned generation and explicit target queries | Do not claim that targeting unfilled regions with an LLM is new |
| [ACES, NeurIPS 2024](https://papers.nips.cc/paper_files/paper/2024/file/7d0c6ff18f16797b92e77d7cc95b3c53-Paper-Conference.pdf) | Goal-directed puzzle generation with executable solution checks | Separate task generation from policy optimization; executable evaluation alone is not a contribution |
| [BehaveSim, v1](https://arxiv.org/html/2603.02787v1) | Behavior-dependent selection and population management | Treat as close prior art, not an adjacent citation |

Internal judgment: the broad architecture is not a defensible novelty claim on current
evidence. The narrower research question remains worthwhile: under a shared bounded
representation and evaluator, does fixed-reference parent weighting change development
utility relative to uniform selection? A positive answer would establish a measured effect
in that setting. It would not by itself establish that the rule is unprecedented or that
OPENEND beats native published methods. A negative result remains informative.

No exact-equivalence or literature-absence verdict is assigned by this review. Differences
in domain or implementation are not sufficient evidence of a novel research contribution.

## Ordered remaining work

1. Complete close-method extraction for ELM, MAP-Elites, FunSearch, EoH, AlphaEvolve and
   BehaveSim: descriptors, parent selection, survival, model/evaluation budgets, evaluation
   access and code/version provenance. Preserve unknown fields as unknown.
2. Follow the recorded backward leads (especially MEoH and LMX), inspect ACES sampler
   details, and complete a dated forward-citation search. Add a stop/scope statement so
   the review has a finite, auditable boundary.
3. Internally adjudicate the claim/source matrix: retained question, rejected originality
   claims, comparator obligations and unresolved equivalences. Close Phase 2 only when
   these deliverables are recorded; external review is not a gate.
4. Enter Phase 3: finalize action eligibility, numerical semantics, reference certificates,
   training/evaluation boundaries, objective aggregation, representation limits and the
   acceptance checklist. Reuse the already completed evaluator audit.
5. Then freeze and execute the Phase 4 adapted-baseline protocol. Native reproduction
   remains explicitly separate.

## Phase 3 requirements already implied by this review

Reference distance, live archive density and requested target descriptors are different
quantities and need distinct names and measurements. A target-generation extension needs
its own controllability check before utility claims. Evaluate behavior on probes not used
for search when testing robustness. Declare proposal, solver, critic and retrieval costs
separately wherever those roles exist. These are design requirements for later work, not
new completed experiments or amendments to the frozen primary contrast.
