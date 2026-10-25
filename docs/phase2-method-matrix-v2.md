# Phase 2 method comparison matrix

> See [technical-review corrections](phase2-technical-review-2026-10-15.md) and [evidence v3](../data/literature/phase2-evidence-v3.json). This v2 matrix is retained for provenance.

Reviewed internally on 2026-10-15. The [structured register](../data/literature/phase2-evidence-v2.json) supplies versions, sections, budget/evaluation fields and limitations. Unknown means not established by this review, not absent from the competing method.

| Method / source | Selection and retention | Relevance |
|---|---|---|
| [map-elites](https://arxiv.org/html/1504.04909v1) | Uniform occupied-archive sampling; Fill empty cell or replace with fitter occupant | Required matched uniform archive control |
| [elm](https://arxiv.org/pdf/2206.08896) | Random inhabited niche; LLM diff mutation; Empty cell or higher-performance champion | Foundational LLM-QD comparison |
| [funsearch](https://www.nature.com/articles/s41586-023-06924-6) | Uniform island; score-based cluster and length-based program sampling; Registration within islands; periodic weaker-island resets | Required strong baseline, explicitly labeled adaptation until native fidelity established |
| [eoh](https://arxiv.org/html/2401.02051v3) | Fitness-rank weights proportional to 1/(rank+population size); Paper retains top N; pinned code additionally deduplicates objectives | Required strong baseline; choose paper or code recipe prospectively |
| [alphaevolve](https://arxiv.org/html/2506.13131v1) | Database resurfaces prior programs; exact probability rule not established; Database inspired by MAP-Elites and islands | Architecture comparison; no native superiority claim |
| [in-context-qd](https://arxiv.org/html/2404.15794v2) | Uniform archive context; uniform or empty-cell-first feature queries; MAP-Elites archive admission | Required conceptual comparator if targeting is reintroduced |
| [aces](https://papers.nips.cc/paper_files/paper/2024/file/7d0c6ff18f16797b92e77d7cc95b3c53-Paper-Conference.pdf) | Uniform target cell; examples from three nearest filled cells; within-cell normalized fitness softmax, temperature 0.2; Valid evaluated puzzles enter descriptor archive | Targeting and grounded-evaluation design comparison |
| [behavesim](https://arxiv.org/html/2603.02787v1) | FunSearch intra/inter-island selection; EoH dominance-dissimilarity probabilities; Trajectory-based islands; EoH dissimilarity-based survival | Priority behavioral-selection comparator before broad mechanism claims |
| [meoh](https://arxiv.org/html/2409.16867v1) | Dominance-masked dissimilarity scores converted by softmax (Appendix A); Truncation by dominance-dissimilarity | Required source comparison; multiobjective experiment only with separate protocol |
| [lmx](https://www.research.autodesk.com/app/uploads/2023/12/Language-Model-Crossover.pdf) | Random multiple parents concatenated for LLM continuation; Illustrated evolutionary loop uses fitness tournaments | Foundational variation comparison |
| [shinkaevolve](https://arxiv.org/html/2509.19349v1) | Fitness sigmoid times inverse offspring count, or rank power law; Evolutionary database; similarity rejection can filter proposals | Priority usage-aware selection comparator before selection-originality claims |
| [dgm](https://arxiv.org/html/2505.22954v1) | Sigmoid performance times inverse functioning-children count; Retain valid agents able to edit codebases | Backward-citation overlap; not a packing baseline |
| [loreley](https://arxiv.org/html/2608.19703v1) | Archive/context policies in matched study; exact sampler not reproduced; Bounded Pareto sets in cells and islands | Design/evaluation comparison; retain possibility of negative results |
| [eps-study](https://arxiv.org/html/2407.10873v1) | Standalone generation and evolutionary-search comparisons; Depends on compared method | Independent generation and simple incumbent-search controls required |
| [hss-meoh](https://github.com/MOL-SZU/HSS-MEoH) | README describes fitness plus offspring-count novelty; Not implementation-audited | Screened additional overlap lead; not an efficacy comparator |
