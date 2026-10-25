# Phase 2 method matrix — reviewed v3

Active evidence: [register v3](../data/literature/phase2-evidence-v3.json). [Technical review](phase2-technical-review-2026-10-15.md). All rows are internal source review, not replications.

| Method | Evidence level | Selection | Limitation |
|---|---|---|---|
| [map-elites](https://arxiv.org/html/1504.04909v1) | selected_primary_method_sections | Uniform occupied-archive sampling | Not reproduced; HTML date anomaly not treated as new publication |
| [elm](https://arxiv.org/pdf/2206.08896) | selected_primary_method_sections | Random inhabited niche; LLM diff mutation | Fine-tuning and later stages not reproduced; token equivalence unknown |
| [funsearch](https://www.nature.com/articles/s41586-023-06924-6) | selected_primary_method_sections | Uniform island; score-based cluster and length-based program sampling | No native reproduction; original model compute not matched |
| [eoh](https://arxiv.org/html/2401.02051v3) | selected_primary_method_sections | Fitness-rank weights proportional to 1/(rank+population size) | Default schedule differs from five-operator paper recipe; upstream M3 implementation exists; native reproduction remains Phase 4 work |
| [alphaevolve](https://arxiv.org/html/2506.13131v1) | selected_primary_method_sections | Database resurfaces prior programs; exact probability rule not established | Exact descriptor/grid and sampler not established from disclosed method; no reproduction |
| [in-context-qd](https://arxiv.org/html/2404.15794v2) | selected_primary_method_sections | Uniform archive context; uniform or empty-cell-first feature queries | Not reproduced; equivalent token costs unknown |
| [aces](https://papers.nips.cc/paper_files/paper/2024/file/7d0c6ff18f16797b92e77d7cc95b3c53-Paper-Conference.pdf) | selected_primary_method_sections | Uniform target cell; examples from three nearest filled cells; within-cell normalized fitness softmax, temperature 0.2 | No packing-equivalence claim; descriptor label hacking discussed by authors; not reproduced |
| [behavesim](https://arxiv.org/html/2603.02787v1) | selected_primary_method_sections | FunSearch intra/inter-island selection; EoH dominance-dissimilarity probabilities | Distance normalization and implementation not reproduced; equal tokens unestablished |
| [meoh](https://arxiv.org/html/2409.16867v1) | selected_primary_method_sections | Dominance-masked dissimilarity scores converted by softmax (Appendix A) | Prose probability wording less precise than appendix; not reproduced |
| [lmx](https://www.research.autodesk.com/app/uploads/2023/12/Language-Model-Crossover.pdf) | selected_primary_method_sections | Random multiple parents concatenated for LLM continuation | Domain-specific settings not reproduced; author-hosted PDF has no immutable version in URL |
| [shinkaevolve](https://arxiv.org/html/2509.19349v1) | selected_primary_method_sections | Fitness sigmoid times inverse offspring count, or rank power law | Whole-system reproduction absent; archive-filter novelty is not literature novelty |
| [dgm](https://arxiv.org/html/2505.22954v1) | selected_primary_method_sections | Sigmoid performance times inverse functioning-children count | No reproduction; benchmark access is not our held-out protocol |
| [loreley](https://arxiv.org/html/2608.19703v1) | selected_primary_method_sections | Archive/context policies in matched study; exact sampler not reproduced | Reported finite-budget results not transferred to OPENEND; no reproduction |
| [eps-study](https://arxiv.org/html/2407.10873v1) | selected_primary_method_sections | Standalone generation and evolutionary-search comparisons | Evaluation counts do not establish token parity; results not replicated |
| [hss-meoh](https://github.com/MOL-SZU/HSS-MEoH) | author_readme_screen_only | README describes fitness plus offspring-count novelty | README-only evidence; publication status, exact formula and implementation not verified |
