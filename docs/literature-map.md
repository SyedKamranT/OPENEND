# Literature map and contribution audit

**Status: CORRECTED / IN PROGRESS (2026-10-08).** This is a targeted primary-source map, not a completed systematic review or replication. The previous unsupported 68% figure, invented titles/author groups, universal competitor-deficit claims, and implemented-feature checkmarks have been withdrawn.

## Closest methodological comparisons

?Not established here? means this review has not established a capability or absence; it is not a negative result about a competing system.

| Work and primary source | Evidence checked | Consequence for OPENEND |
|---|---|---|
| [Novelty Search](https://pubmed.ncbi.nlm.nih.gov/20868264/) | Foundational novelty-as-search-objective work; detailed replication pending | Explicit novelty search itself is established prior art. |
| [MAP-Elites](https://arxiv.org/abs/1504.04909) | Feature-indexed quality/diversity archive, abstract and method identity | A QD archive is a baseline component, not our claimed invention. |
| [ELM](https://arxiv.org/abs/2206.08896) | Abstract: LLM program mutation combined with MAP-Elites | Combining LLM mutation and QD is already demonstrated. |
| [FunSearch](https://www.nature.com/articles/s41586-023-06924-6) | Methods: executable evaluation, islands, program signatures/clustering | Preserve its diversity mechanisms when defining a faithful comparator; no unsupported collapse claim. |
| [AlphaEvolve](https://arxiv.org/html/2506.13131v1) | Section 2.5: database inspired by MAP-Elites plus island populations | QD-style storage is a close overlap; calling it only fitness pools is inadequate. |
| [LLMatic](https://arxiv.org/abs/2306.01102) | Abstract: code-model variation and QD for neural architecture search | Add to LLM-QD related work; domain and representation differ. |
| [QDAIF](https://arxiv.org/abs/2310.13032) | Abstract: language-model variation and quality/diversity feedback for text | LLM-driven QD is not confined to executable domains. |
| [EoH](https://arxiv.org/abs/2401.02051) | Abstract: joint thought/code heuristic evolution, including bin packing | A particularly relevant future strong heuristic-search baseline. |
| [BehaveSim](https://arxiv.org/abs/2603.02787) | Abstract: intermediate problem-solving trajectories, similarity and diversity in algorithm design | Behavioral diversity and algorithmic similarity require direct comparison; our finite decision probes are much simpler. |
| [Loreley](https://arxiv.org/abs/2608.19703) | Abstract: repository-state QD and a matched comparison, August 2026 preprint | Current repository-level search work must be included; not independently replicated here. |
| [Idea Novelty Checker](https://aclanthology.org/2025.sdp-1.9/) | Abstract: retrieval, embedding filtering, and facet-based reranking | Multi-stage evidence retrieval alone is not an original contribution. |

## Adjacent discovery and evaluation work

| Work | Verified scope / relevance | Limitation of our inference |
|---|---|---|
| [The AI Scientist](https://arxiv.org/abs/2408.06292) | Automated research and manuscript workflow | Its limitations do not demonstrate OPENEND superiority. |
| [Co-Scientist](https://www.nature.com/articles/s41586-026-10644-y) | Multi-agent hypothesis development with experimental applications | Experimental biology is not the same evaluation setting as this pilot. |
| [Robin](https://www.nature.com/articles/s41586-026-10652-y) | Multi-agent scientific-discovery workflow integrating literature and experiments | No claim that our bounded policy search subsumes its capabilities. |
| [Nova](https://arxiv.org/abs/2410.14255) | Iterative planning and retrieval for idea generation | Its name is not the invented acronym expansion in the old bibliography. |
| [RQ-Bench](https://arxiv.org/abs/2606.12071) | Model/expert disagreement on research-question novelty | Does not establish a 68% paraphrase-induced error rate in our domain. |
| [LiveIdeaBench](https://www.nature.com/articles/s41467-026-70245-1) | Divergent thinking for scientific ideas with minimal context | Idea ratings do not establish executable algorithmic improvement. |
| [Structured recombination](https://aclanthology.org/2026.tacl-1.20/) | Structured transformations for creative generation, demonstrated with recipes | Recombination is established; algorithmic utility needs separate evaluation. |
| [Human ideation study](https://arxiv.org/abs/2409.04109) | Blinded comparisons involving NLP researchers | Human novelty and feasibility judgments need careful study design and do not transfer automatically to bin packing. |

## Candidate contribution, still unproven

A defensible prospective contribution is an empirically supported incremental effect of fixed-corpus sparse targeting over otherwise matched QD/evolutionary search, with independent evidence-based novelty adjudication and objective success. The current implementation tests only a bounded behavioral-policy version of the search mechanism. It has no comprehensive novelty corpus or positive novelty adjudicator.

The primary contrast keeps QD, generation, model, and evaluator fixed while changing parent selection. An observed difference would characterize this implementation and task suite, not establish that the overall architecture is unprecedented. A negative or inconclusive comparison is retained.

## Phase 2 completion requirements

For each close paper, record exact version, method sections, descriptors, variation and parent-selection rules, evaluation access, compute accounting, source/code availability, and a concrete difference from the proposed method. Read full methods and relevant appendices for abstract-only entries. Search forward/backward citations and document search dates and inclusion rules. Reproduce the closest available methods where feasible. Expand the table only with evidence; neither blank cells nor lack of reporting prove absence.

The corrected bibliography is in `paper/references.bib`. Some large author lists are explicitly abbreviated using BibTeX `and others`; no placeholder research groups are treated as actual authors. Venue-level publication versions should be preferred over preprints when final submission metadata is prepared.
