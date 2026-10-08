# OPENEND research and repository review

Review date: 2026-10-08 (Asia/Calcutta). Scope: `phases.md`, `OPENEND_PROJECT_CONTEXT.md`, the supplied Gemini handoff, all six research documents, the manuscript and bibliography, configurations, packaging, source scaffolding, and existing tests. This is a review of the current work, with a targeted primary-source literature audit; it is not a completed systematic literature review or a replication of cited experiments.

**Verdict: retain the research direction and repository scaffold; reopen Phase 1. The claim that research is frozen, scientifically verified, and production-ready is not supported.** Phase 2 literature work can proceed as part of repairing the research specification. Confirmatory experiments should wait for a consistent protocol and validated evaluator.

The original files have been preserved. Recommendations in this report are proposed changes, not silently adopted experimental decisions.

## 1. What is actually complete

The project has a useful question, five hypothesis drafts, an appropriate initial emphasis on executable algorithmic tasks, a baseline taxonomy, an artifact layout, configuration sketches, and research-governance intentions. Explicitly restricting novelty to a corpus and requiring objective utility are sound starting principles.

The implementation consists of package initialization files containing docstrings. There is no implemented generator, search loop, corpus index, verifier, sandbox, benchmark, statistical analysis, or experiment runner. Data and results contain placeholders rather than research evidence. This is acceptable for an early research scaffold; it does not substantiate production or validation claims.

Verification performed:

- `python -m pytest -q`: **4 passed**, with a pytest cache-permission warning. Python was 3.11.6 and pytest was 8.4.2, whereas the dependency file specifies pytest 8.0.2. This was a test in the available environment, not a clean installation from the dependency file.
- Inspection of `tests/unit/test_phase1_lock.py`: tests check directory existence, document existence/size, YAML parsing, and selected strings. They do not test scientific consistency, citation accuracy, budget equivalence, containment, or reproducibility.
- `importlib.util.find_spec('src.orchestration.cli')` returned `None`. The advertised console entry point in `pyproject.toml:71` has no target module.
- Git inspection: HEAD was `592c544`; only `phases.md` and `OPENEND_PROJECT_CONTEXT.md` were tracked at review time. The new scaffold was untracked. Thus the current commit does not capture the claimed research lock. Git was inspected using a command-scoped safe-directory option; no global Git configuration was changed.

No model API calls, generated-code execution, dependency installation, publication, or research experiment was performed.

## 2. Findings that block a defensible research lock

### R1 — The manuscript asserts results that do not exist

**Evidence:** `paper/main.tex:20` says OPENEND achieves significantly higher NSR than matched baselines and prevents failure modes. No corresponding experimental artifacts exist.

**Required correction:** Change the abstract to proposal language and mark results as pending. Remove assertions of established benchmarks, superiority, and prevention until supported by frozen evidence. The original context explicitly says to write claims from results.

### R2 — Bibliographic metadata is substantially incorrect

**Evidence:** `paper/references.bib` and `docs/literature-map.md:65` contain titles and author groups that do not match the linked publications. These are substantive attribution errors, not just formatting problems.

The following corrections were verified against publisher or arXiv records. Author names below are abbreviated for this audit, not complete replacement BibTeX entries.

| Existing key | Verified publication / attribution | Correction needed |
|---|---|---|
| `alphaevolve2025` | Novikov et al., [AlphaEvolve: A coding agent for scientific and algorithmic discovery](https://arxiv.org/abs/2506.13131), 2025 | Replace title and fabricated collective-author formatting. |
| `nova2024` | Hu et al., [Nova: An Iterative Planning and Search Approach to Enhance Novelty and Diversity of LLM Generated Ideas](https://arxiv.org/abs/2410.14255), 2024 | Replace the invented acronym expansion and author attribution. |
| `coscientist2026` | Gottweis et al., [Accelerating scientific discovery with Co-Scientist](https://www.nature.com/articles/s41586-026-10644-y), Nature 655, 487–496 (2026) | Replace title, authors, volume, and pages. |
| `robin2026` | Ghareeb et al., [A multi-agent system for automating scientific discovery](https://www.nature.com/articles/s41586-026-10652-y), Nature 655, 497–505 (2026) | Replace title, authors, volume, and pages. |
| `novelty2025sdp` | Shahid et al., [Literature-Grounded Novelty Assessment of Scientific Ideas](https://aclanthology.org/2025.sdp-1.9/), SDP 2025, 96–113 | Replace title, placeholder authors, and pages. |
| `liveideabench2026` | Ruan et al., [Evaluating LLMs' divergent thinking capabilities for scientific idea generation with minimal context](https://www.nature.com/articles/s41467-026-70245-1), Nature Communications 17, article 3625 (2026) | Replace title, placeholder authors, and article number. The DOI suffix is not the article number. |
| `rqbench2026` | Sinhahajari, Majumder, and Poria, [On the Limits of LLM-as-Judge for Scientific Novelty Assessment](https://arxiv.org/abs/2606.12071), 2026 | Replace invented title and author group. This is an arXiv paper, not the Nature Communications article. |
| `structuredrecombination2026` | Mizrahi et al., [Cooking Up Creativity: Enhancing LLM Creativity through Structured Recombination](https://aclanthology.org/2026.tacl-1.20/), TACL 14, 418–441 (2026) | Replace title, placeholder authors, and pages. |

The FunSearch, AI Scientist, and MAP-Elites identities match the linked records at the title level; this does not certify every field of every remaining entry. Import publisher metadata and validate every entry before publication.

`docs/literature-map.md:56` additionally asserts novelty overestimation of “up to 68%” under terminology changes. I did not locate support for that specific claim in the cited RQ-Bench and LiveIdeaBench pages or the RQ-Bench full text. Remove the number unless an exact supporting result can be identified. RQ-Bench reports disagreement between model and expert assessments of research questions; that does not establish a quantified failure rate for OPENEND's algorithmic domain or for each named competing system. [RQ-Bench full text](https://arxiv.org/html/2606.12071)

### R3 — The claimed research gap overlooks close prior work

**Evidence:** The comparative matrix and discussion in `docs/literature-map.md:33` imply that competing systems largely lack the diversity mechanisms OPENEND proposes.

- AlphaEvolve explicitly describes a program database inspired by both MAP-Elites and island populations, in section 2.5. The description “Partial (Fitness pools)” obscures this close overlap. [AlphaEvolve methods](https://arxiv.org/html/2506.13131v1)
- FunSearch explicitly uses islands and program clustering to preserve diversity. The claim that it rapidly collapses to superficial variants is not demonstrated by the current review. [FunSearch methods](https://www.nature.com/articles/s41586-023-06924-6)
- **Evolution through Large Models (ELM)** already combines language-model program mutation with MAP-Elites. It is a necessary comparator for any claim about LLM-driven QD. [ELM](https://arxiv.org/abs/2206.08896)
- **LLMatic** studies language models with QD for architecture search; **QDAIF** studies language-model variation and quality/diversity feedback. Both belong in the gap analysis. [LLMatic](https://arxiv.org/abs/2306.01102), [QDAIF](https://arxiv.org/abs/2310.13032)
- **BehaveSim** addresses algorithmic similarity through intermediate execution trajectories and integrates it into algorithm-design systems. This is particularly close to OPENEND's representation and diversity problem. [BehaveSim](https://arxiv.org/abs/2603.02787)
- **Loreley**, submitted in August 2026, retains repository candidates in a QD archive and compares search policies under a matched experimental design. Include it in the current literature search, while distinguishing preprints from independently replicated evidence. [Loreley](https://arxiv.org/abs/2608.19703)
- The **Idea Novelty Checker** already combines retrieval, embedding filtering, and facet-based reranking for novelty assessment. Multi-stage retrieval-based novelty checking alone is not a new contribution. [Shahid et al.](https://aclanthology.org/2025.sdp-1.9/)

**Required correction:** Replace unsupported checkmarks and blanket deficit claims with source-located evidence, “not reported,” and “not assessed.” Mark OPENEND features as proposed. A defensible candidate contribution is the measured incremental value of corpus-relative sparse targeting, with independent novelty auditing, over strong existing evolutionary/QD methods. Whether that contribution is novel remains open.

### R4 — The nominal budgets and comparison conditions conflict

| Item | Research specification / baseline | Full system / other document |
|---|---|---|
| Candidate allowance | 100 per task/seed | 50 generations × 10 candidates = 500 configured slots |
| Token ceiling | 500,000 in research question; no total-run ceiling in baseline YAML | 10,000,000 in full YAML |
| Execution timeout | 10 seconds per evaluation in baseline YAML | 15 seconds in full YAML; protocol says 10 seconds per test case |
| Seeds | Five listed in baseline YAML and protocol | One listed in full YAML; H2 specifies ten |
| QD grid | B7 uses two descriptors and 100 cells | Full system specifies 600 cells with a different descriptor scheme; QD YAML has capacity 500 |
| H3 target | Greater than 50% false-positive reduction | At least 40% of naive novelty claims debunked; a different quantity |
| Overlap screening | 10-grams in research question | 12-token overlap in protocol |
| Primary statistics | Mann–Whitney plus Bonferroni in research question | Paired bootstrap in H4; Holm in protocol |

Sources: `configs/baseline.yaml`, `configs/full_openend.yaml`, `configs/qd.yaml`, and the three core research documents. These are **configured allowances**, not evidence of resources actually consumed.

**Required correction:** Use one shared, validated experiment specification. Match the generator model and shared components for causal comparisons. Account for prompts, completions, billed reasoning where available, retries, critique, mutation, verifier calls during search, retrieval/embedding overhead, and evaluator compute. Report actual consumption and cost. Equal token counts across different proprietary models do not establish equal FLOPs.

Use common resource ceilings with a predefined stopping rule; different methods need not consume identical numbers of calls to be comparable. Separate search costs from a common final audit, report both, and keep audit effort equal across systems.

### R5 — Statistical non-significance is incorrectly called falsification or equivalence

**Evidence:** `docs/research-question.md:123` uses `p > 0.05` as evidence of compute-neutral equivalence. H1, H4, and H5 similarly interpret failure to establish superiority as falsification.

A wide interval spanning harmful and useful effects is inconclusive. Equivalence requires a predefined practical margin and an appropriate interval or equivalence test. Statistical significance also does not establish practical importance. [ASA statement](https://doi.org/10.1080/00031305.2016.1154108)

Candidates within adaptive search runs are dependent. Seeds on the same task do not create additional independent task families. The protocol must define the estimand, task weighting, paired comparisons, unit of replication, and resampling hierarchy. Mann–Whitney tests independent distributions; it does not directly implement the mean-difference hypotheses currently written or exploit a paired design. [SciPy reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html)

The seed conflict is consequential: with five nonzero independent pairs, the smallest exact two-sided Wilcoxon signed-rank p-value is `2/2^5 = 0.0625`. Five pairs cannot meet an exact per-task threshold of 0.01, even before multiplicity correction.

**Required correction:** Make H4 the primary discovery hypothesis; distinguish supporting, negative, and inconclusive outcomes. Predefine a useful effect size, primary comparator, comparison family, and paired run/task analysis. Determine sample size using a development pilot and power/precision analysis, not an arbitrary seed count. Do not pool all candidate rows as independent observations. A 10,000-resample bootstrap does not compensate for too few independent tasks.

### R6 — Novelty is partly defined by the metric the method optimizes

**Evidence:** `docs/research-question.md:32` makes low embedding similarity a necessary condition for corpus novelty, while H1 rewards increased embedding distance. No calibration data, equivalence rubric, or independent final adjudication is specified.

An algorithm can be substantively different yet close in embedding space. Renaming, dead code, and unrelated prose can increase distance without changing the mechanism. Optimizing the same distance used to declare success risks measuring metric exploitation.

**Required correction:** Separate the search proxy from the final verdict. Use semantic and lexical scores to retrieve evidence, then assess mechanism-level equivalence under a frozen rubric. Define verdicts such as equivalent prior art found, no equivalent found under the protocol, and unresolved. An empty retrieval result must be distinguishable from a failed or incomplete search.

Apply the same independent final verifier to **all** systems, including the “without verifier” ablation. Removing a verifier from search must not remove it from outcome measurement. Calibrate on independently labeled prior-art pairs and hard paraphrase examples before final experiments.

### R7 — A 2024 retrieval cutoff does not prevent model-training contamination

**Evidence:** `docs/research-question.md:106` and `README.md:94` make strong leakage-prevention claims. The configuration uses models released after the corpus cutoff. The 10-gram audit is said to guarantee no memorized regurgitation.

Restricting retrieval cannot erase knowledge in pretrained weights. Lexical checks miss rewritten memorized solutions and can flag common legitimate code. A corpus snapshot also needs document versions, dates, licenses, checksums, inclusion rules, and a real manifest; none exists yet.

**Required correction:** Distinguish corpus novelty, training-data contamination risk, and broader historical novelty. Retain overlap checks as diagnostics, not guarantees. Use development/final task separation, held-out instance distributions, and provenance audits. Where feasible, use documented training cutoffs for historical reconstruction; otherwise explicitly limit independence claims.

A contemporary prior-art audit can detect post-2024 rediscoveries, but its findings must be reported separately from the frozen-corpus score. Do not mix live web results silently into an allegedly immutable benchmark.

### R8 — The verifier experiment has no independent truth standard

**Evidence:** H3 treats whatever the adversarial search rejects as a false novelty claim and requires debunking a fixed fraction of all naive-positive candidates.

That fraction depends on the pool's prevalence of known ideas. A better generator can reduce it even with a better verifier. An indiscriminate rejector can appear effective if recall of corpus-novel cases is not measured.

**Required correction:** Freeze a shared evaluation pool with independently adjudicated, corpus-relative labels, including known equivalents, difficult rewrites, distinct mechanisms, and unresolved cases. Compare verifier methods on paired items. Measure false novelty, missed novelty, abstention, evidence validity, retrieval recall where assessable, and cost. Compare at a defined recall/coverage requirement; cluster uncertainty by source idea or task as appropriate. Keep this verifier study separate from the search-yield study.

### R9 — NSR does not yet measure distinct discoveries reliably

**Evidence:** The primary denominator is all generated candidates as a multiset, but repeated successes can repeatedly count in the numerator. Failed parses, retries, incomplete audits, and multi-candidate completions have no accounting specification.

**Required correction:** Keep all generated attempts and failures in the event history. Define the candidate unit and API-failure policy before experiments. Report attempt-level NSR alongside distinct validated mechanism yield at fixed budget and the duplicate rate. Zero generated candidates or zero naive-positive judgments produce undefined rates, not silent zeroes. Report unresolved novelty explicitly, with conservative bounds or a prespecified handling rule.

Define **what is being discovered**: the algorithm, its output artifact (such as a graph construction), or both. Identical input/output behavior does not prove identical algorithms; different implementations of a known algorithm are not automatically new mechanisms. Deduplication needs task-specific evidence, not output hashes alone. BehaveSim provides relevant prior work, not a complete universal equivalence solution. [BehaveSim](https://arxiv.org/abs/2603.02787)

### R10 — The benchmark and representation are not operationally specified

Four broad task families are listed, but there is no selected task contract, development/validation/test split, executable success threshold, reference baseline, or calibration procedure. Concurrent lock-free data structures and asymptotic complexity claims require substantially more than ordinary unit tests. Runtime medians are measurements, not guaranteed identical values across machines.

`configs/exploration.yaml` specifies UMAP and k-neighbor distance without a fitted reference population, normalization, model revision, calibration, or a mapping from target locations back to program generation. The equation called density is actually a mean neighbor-distance **sparsity score**: larger values mean more sparse. Applying inverse weighting directly to it would favor dense regions. Percentile direction must be made explicit.

`configs/qd.yaml` mixes a CVT-like label (`cvd_map_elites`) with grid dimensions and inconsistent capacity. Behavioral descriptors such as algorithmic paradigm and asymptotic class lack deterministic extraction procedures. They are not established orthogonal axes.

**Required correction:** Start with one tractable pilot task family, then expand for generalization. Specify inputs, candidate interface, constraints, objective, reference solutions, hidden instances, success margins, descriptors, novelty unit, and evaluator failure states. Prefer measurable behavioral descriptors over unverified complexity labels. Freeze the representation and transformation before final testing; assess sensitivity using representations not optimized by the search.

### R11 — Sandbox and immutable telemetry are intentions, not implemented guarantees

**Evidence:** `docs/experimental-protocol.md:94` relies on a subprocess and virtual environment while promising no sockets and bounded resources. No enforcement implementation exists. A Python virtual environment isolates dependencies; it is not an OS security boundary. [Python documentation](https://docs.python.org/3.11/library/venv.html)

The JSON blocks are illustrative records, not schemas. The event example contains a literal `...` in an array and cannot parse as JSON. Placeholders are acceptable only when labeled as examples. There are no validators or enforced run/candidate links, prompt artifacts, complete retrieval records, error states, or storage-integrity controls.

**Required correction:** Before evaluating generated code, implement and verify OS-level containment for the selected runtime: network denial, filesystem boundaries, unprivileged execution, resource limits, child-process cleanup, and evaluator integrity. Validate escape attempts against those controls. Define typed manifests and events, artifact hashes, persisted prompts/responses/retrieval evidence, and explicit failure outcomes. Hashes identify content; immutability additionally needs an enforced storage and versioning policy.

### R12 — Reproducibility and packaging are incomplete

`requirements.lock` pins a selection of packages but is not a demonstrated complete resolver-generated lock. For example, Click and pytest's Packaging/Pluggy/Iniconfig dependencies are not pinned there. Build requirements remain ranged, optional ML dependencies are not locked, and the configured UMAP package is undeclared. Installing the listed packages may let a resolver obtain additional versions; it is not a fully specified environment.

The package is named `src`, and the missing CLI target prevents the declared command from working. A conventional `src/openend/` layout would avoid exporting a generic package name. Some experiment/analysis directories have no persistent files, so their local presence is not a fresh-clone guarantee.

**Required correction:** Remove or implement the promised CLI, generate the environment lock from a resolver for an explicitly supported interpreter/platform, and check installation plus a small deterministic evaluator example in a clean environment. Preserve raw model outputs to permit replay; distinguish replay reproducibility from reissuing stochastic hosted-model requests. Validate current model access before locking a run; this review did not verify provider availability. Confirm the repository URL and author metadata in `CITATION.cff` before release.

### R13 — Publication criteria introduce positive-result selection

**Evidence:** `docs/publication-plan.md:57` requires all five hypotheses to achieve their statistical standards before release. The original context explicitly permits rigorous negative results.

**Required correction:** Base release on methodological completeness, reproducibility, evidence quality, and honest scope, not whether every hypothesis succeeds. Replace absolute “zero unhandled exploits” with documented testing, scope, and treatment of identified weaknesses. A benchmark bug found after data collection requires a versioned amendment and rerun of affected comparisons, not permanent preservation of an invalid evaluator. Preserve the original runs and explain the change.

Human-study planning also needs recruitment/qualification, sample size, candidate selection, equal selection budgets, randomization, instructions, disagreement handling, and any applicable ethics review. An ordinal model needs candidate/task dependencies as well as rater effects. A feasibility margin on a 1–5 mean scale is not automatically an ordinal-logit coefficient margin. Kendall's W and Krippendorff's alpha are not interchangeable pass/fail substitutes. API energy/carbon estimates should disclose assumptions and uncertainty; token counts do not directly measure provider energy use.

This audit does not verify the conference deadlines recorded in the original planning files or endorse their venue-specific requirements. Those need current official calls for papers when submission planning becomes relevant.

### R14 — Roadmap authority and status are inconsistent

`phases.md` uses Phases 1–18; the context file uses 0–17 with a different grouping; README compresses the work into 12 phases. QD, mutation, verification, and metrics appear both inside early prototypes and as later additions.

**Required correction:** Use `phases.md` as the canonical numbering for this project and map the other roadmaps to it. Distinguish minimum implementations needed for valid early evaluation from later extensions. A baseline novelty evaluator must exist before reporting NSR, even if a more advanced verifier is built later. Freeze the confirmatory protocol after literature review, benchmark calibration, and a separate pilot, before inspecting final outcomes.

## 3. Assessment of the nine Phase 1 requirements

| Requirement | Assessment |
|---|---|
| Research question | Coherent draft; narrow to the incremental effect of sparse targeting. |
| Four to six hypotheses | Five drafted; statistical interpretation and H3 measurement need repair. |
| Operational novelty | Corpus-relative intent is sound; equivalence, calibration, unknowns, and contamination remain unresolved. |
| First domain | Algorithmic/software scope chosen; a runnable first task family is not selected. |
| Metrics | Named and partly formalized; accounting, independence, duplicate handling, and normalization are missing. |
| Baselines | Taxonomy useful; close prior work missing and configurations are confounded. |
| Experimental protocol | Illustrative specification; contradictory budgets/seeds and no executable enforcement. |
| Leakage rules | Helpful intentions; current guarantees are invalid and corpus provenance is absent. |
| Success/failure criteria | Present but logically and statistically inconsistent; practical margins and precision requirements missing. |

**Gate assessment: draft assembled, gate not passed.** A future benchmark implementation is not required merely to write Phase 1, but Phase 1 must accurately separate settled choices, provisional parameters, implementation requirements, and demonstrated evidence.

## 4. Recommended scientific direction

Proposed narrower research question:

> Under a fixed model and resource budget, does targeting low-density regions of a frozen representation of known algorithmic mechanisms increase independently verified, distinct corpus-novel successful solutions compared with otherwise matched evolutionary and quality-diversity search?

This retains the project's ambition while making the mechanism testable. It does not claim that distance from a corpus is distance from all human knowledge. A fixed task suite also does not, by itself, demonstrate indefinite open-ended invention; “OPENEND” can remain the project name while the empirical claim stays narrower.

For a pilot, I recommend online bin-packing heuristic design: it admits a compact candidate interface, exact feasibility checks, known simple references, and different hidden instance distributions. FunSearch provides a relevant prior implementation and result, which also makes it a demanding comparison rather than an untouched domain. This is a reviewer recommendation, not a frozen task decision. [FunSearch](https://www.nature.com/articles/s41586-023-06924-6)

Use one generator model for mechanism comparisons and the same initial candidates, variation operators, available information, evaluation budget, and final auditing protocol. Evaluate this minimal factorial design:

| Condition | QD archive | Sparse-region targeting |
|---|---|---|
| Matched evolutionary control | Off | Off |
| Sparse evolutionary variant | Off | On |
| Standard QD control | On | Off |
| OPENEND minimal variant | On | On |

Preserve B1 and B3 as practical reference baselines. Use an adequately tuned QD implementation and behavioral-diversity competitor; do not claim to reproduce FunSearch or AlphaEvolve from a generic mutation loop. The primary mechanistic contrast is OPENEND minimal versus matched QD; the factorial interaction tests whether sparsity gains depend on QD. Larger-model and multi-agent comparisons belong in separate analyses.

Use a common final outcome pipeline: correctness, hidden-instance utility, mechanism deduplication, and evidence-grounded corpus-relative novelty audit. Search-time audit feedback is a separate experimental factor. The evaluator is retained for all ablations, including “no objective evaluator” in the original context: that can mean no execution feedback during search, not no final validity measurement.

Measure attempt-level NSR, distinct validated discoveries per fixed budget, best utility, coverage on a common fixed descriptor grid, and cost. Normalize QD fitness and fix hypervolume scales/reference points before testing. Similarity increases or human surprise alone do not establish algorithmic discovery.

## 5. Repair order and acceptance evidence

1. **Correct status and claims.** Reclassify Phase 1 as provisional; remove nonexistent results; replace faulty citations and unsupported literature assertions. Acceptance: every empirical assertion has a traceable source or is explicitly a hypothesis.
2. **Validate the gap.** Read the closest program-search, LLM-QD, behavioral-similarity, and novelty-verification papers. Add ELM, LLMatic, QDAIF, BehaveSim, Loreley, EoH, and human ideation evaluation to the candidate reading list. Acceptance: method-level differences and missing evidence are documented; combinations of familiar components are not automatically claimed as inventions. [EoH](https://arxiv.org/abs/2401.02051), [human ideation study](https://arxiv.org/abs/2409.04109)
3. **Choose and build the first benchmark.** Create a small task contract, reference solutions, containment, objective evaluator, and corpus manifest. Acceptance: known valid/invalid candidates and prior-art cases are scored correctly; hidden evaluation data remain outside search access.
4. **Calibrate using development data.** Establish novelty thresholds/rubric, representation, descriptor extraction, verifier performance, and plausible effect/variance estimates. Acceptance: calibration artifacts and unresolved decisions are recorded separately from final tasks.
5. **Lock one coherent confirmatory protocol.** Resolve models, budgets, accounting, comparisons, task/seed sample size, practical margins, human-study scope, and statistics. Acceptance: human-readable documents and validated configuration agree, and a versioned snapshot identifies them.
6. **Run the smallest controlled study.** Implement matched baselines and the minimal sparse/QD variants, then expand only if evidence warrants it. Acceptance: complete logs, measured costs, independent final auditing, and reproducible analysis, including failures and inconclusive results.

Current evidence cannot answer whether OPENEND outperforms baselines, whether it generates new mechanisms, whether the verifier reduces false novelty, or whether experts prefer its outputs. Those remain experimental questions. The work so far establishes a research proposal and scaffold; the next milestone is a credible measurement system and a defensible comparison.
