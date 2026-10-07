# OPENEND — Open-Ended Novelty Discovery Agent

## IDE / AI Agent Context File

**Project status:** Research program — initial stage
**Date initialized:** 2026-10-07
**Working name:** OPENEND
**Primary objective:** Build and scientifically evaluate an autonomous multi-agent system that deliberately explores underrepresented regions of conceptual/solution space to generate, verify, evolve, and validate high-value ideas that are not readily identifiable in existing knowledge.

---

## 1. What We Are Trying to Achieve

We are **not** trying to build a chatbot that simply says “be creative.”

We are investigating a harder research problem:

> **Can an AI agent deliberately search beyond dense regions of existing human knowledge and discover useful, experimentally validated ideas that are both novel relative to a frozen knowledge corpus and difficult for standard LLM prompting/retrieval systems to produce?**

The central thesis is that novelty should be treated as a **search objective and system-level property**, not merely as a property of one LLM-generated sentence.

The proposed system combines ideas from:

- LLM-based research agents
- autonomous scientific discovery
- novelty search
- quality-diversity optimization / MAP-Elites
- evolutionary search
- structured idea recombination
- retrieval and prior-art search
- adversarial novelty verification
- simulation / executable evaluation
- human expert evaluation

The first implementation should focus on **software/algorithmic invention**, because candidate ideas can be evaluated automatically with executable tests or benchmarks without requiring a physical laboratory.

---

## 2. The Exact Research Gap

Existing work has demonstrated important pieces:

- LLMs can generate research ideas that humans sometimes judge novel.
- Iterative planning and external search can improve idea novelty.
- FunSearch and AlphaEvolve demonstrate LLM-guided evolutionary discovery of useful algorithms/programs.
- AI Scientist demonstrates end-to-end automated research loops.
- Co-Scientist demonstrates multi-agent generation, critique, ranking, and evolution of scientific hypotheses.
- Robin demonstrates hypothesis → experiment → observation → revised hypothesis loops.
- Novelty Search and MAP-Elites provide older but important foundations for explicitly exploring novelty/diversity.
- Recent work shows that LLM-as-judge novelty assessment can produce a “novelty mirage,” where models overestimate how novel ideas actually are.

The proposed gap is **not** “Can LLMs generate novel ideas?”

The target gap is:

> **A general discovery architecture that explicitly identifies underrepresented regions of a knowledge/solution space, directs generation toward those regions, preserves quality-diverse candidates, adversarially searches for prior art, and validates surviving candidates through executable or experimental tests.**

The contribution must be demonstrated experimentally rather than asserted.

---

## 3. Core Research Questions

### RQ1 — Exploration
Can explicit conceptual/solution-space exploration produce ideas that are more novel and diverse than ordinary LLM sampling or RAG?

### RQ2 — Quality-diversity
Can novelty-driven search maintain useful diversity without collapsing into nonsensical outputs?

### RQ3 — Novelty verification
Can multi-stage, adversarial prior-art checking reduce false novelty claims compared with a single LLM judge?

### RQ4 — Discovery
Can the system produce candidates that are both novel relative to the frozen corpus and objectively useful under an executable evaluator?

### RQ5 — Human surprise
Do domain experts judge the best surviving candidates as meaningfully more surprising/unexpected than baseline systems?

### RQ6 — Search mechanism
Which components create the gain: sparse-region targeting, structured mutation, cross-domain recombination, quality-diversity selection, adversarial verification, or their combination?

---

## 4. Main Hypotheses

**H1 — Exploration hypothesis**  
Explicit low-density/sparse-region exploration increases semantic and expert-rated novelty over standard generation.

**H2 — Quality-diversity hypothesis**  
A quality-diversity archive produces a better novelty–utility frontier than quality-only optimization.

**H3 — Verification hypothesis**  
Adversarial, multi-source novelty verification reduces false novelty claims compared with LLM-as-judge alone.

**H4 — Discovery hypothesis**  
The proposed system achieves a higher **Novel-Success Rate** than baseline systems.

**H5 — Surprise hypothesis**  
Experts rate the system’s best surviving discoveries as more surprising than baseline outputs while maintaining comparable or better feasibility.

---

## 5. Critical Definition: We Must Not Claim “Never Invented in Human History”

Absolute global novelty is generally impossible to prove.

The paper should use operational definitions such as:

> **Corpus-novel:** no substantially equivalent prior art was identified within the frozen search corpus and search protocol.

> **Semantically novel:** the idea is sufficiently distant from retrieved prior art according to predefined semantic/structural measures.

> **Validated novel-success:** the candidate is corpus-novel under the protocol and passes the objective task evaluator.

Only use stronger language if historical or experimental evidence supports it.

Never equate “not found on the web” with “never existed.”

---

## 6. Initial Domain: Algorithmic / Software Invention

The first research implementation should avoid dependence on physical laboratories.

Primary candidate domain:

> **Algorithm and software invention**

Why:

- candidates can be represented structurally;
- mutations can be executed;
- performance can be benchmarked;
- correctness can often be tested automatically;
- failures provide objective feedback;
- the discovery loop can run many generations;
- reproducibility is easier than in physical experimentation.

Possible task families:

1. Algorithm design under constrained objectives.
2. Optimization heuristics.
3. Data-structure variants.
4. Scheduling / routing algorithms.
5. Search algorithms.
6. Code-generation strategies.
7. Program optimization.
8. Small mathematical/computational construction problems.
9. Synthetic problems where the ground-truth optimum or strong reference is known.

We should not start by claiming that OPENEND can invent arbitrary physical products. First establish the mechanism in a domain with reliable automated validation.

---

## 7. Proposed System Architecture

```text
                         USER PROBLEM
                              |
                              v
                    +--------------------+
                    | Problem Decomposer  |
                    +---------+----------+
                              |
                 +------------+------------+
                 |            |            |
                 v            v            v
              Goals      Constraints     Domain
                 |            |            |
                 +------------+------------+
                              |
                              v
                    FROZEN KNOWLEDGE CORPUS
                              |
                    papers / patents / code
                              |
                              v
                     KNOWLEDGE REPRESENTATION
                              |
                    embeddings + graph/features
                              |
                +-------------+-------------+
                |                           |
                v                           v
         Dense regions                 Sparse regions
                |                           |
                |                           v
                |                   EXPLORATION AGENTS
                |                           |
                |              +------------+------------+
                |              |            |            |
                |              v            v            v
                |          Mutation     Contradiction  Cross-domain
                |              |            |         recombination
                |              +------------+------------+
                |                           |
                +-------------+-------------+
                              v
                       IDEA POPULATION
                              |
                    +---------+---------+
                    |         |         |
                    v         v         v
                 Novelty   Utility   Feasibility
                    |         |         |
                    +---------+---------+
                              |
                              v
                       QUALITY-DIVERSITY
                        ARCHIVE / MAP
                              |
                              v
                  ADVERSARIAL PRIOR-ART SEARCH
                              |
              +---------------+----------------+
              |               |                |
              v               v                v
           Literature      Patents         Code/products
              |               |                |
              +---------------+----------------+
                              |
                              v
                       NOVELTY VERDICT
                              |
                              v
                  EXECUTABLE / SIMULATION TEST
                              |
                     +--------+--------+
                     |                 |
                  failure            success
                     |                 |
                   mutate            archive
                     |                 |
                     +--------+--------+
                              |
                              v
                       NEXT GENERATION
```

This architecture is a research hypothesis, not a claim that every component must survive to the final system. Ablations will determine which components are actually useful.

---

## 8. System Components

### 8.1 Problem Decomposer
Input: natural-language problem.

Output:

```text
problem_statement
objective
constraints
success_metrics
known_solution_classes
search_domain
candidate_representation
```

### 8.2 Knowledge Corpus
Create a **time-frozen corpus** for evaluation.

Potential sources:

- arXiv / Semantic Scholar / OpenAlex metadata and papers where legally usable;
- patent metadata / patent full text where licensing permits;
- public code repositories where redistribution/licensing permits;
- benchmark documentation;
- selected technical sources.

Important: record an explicit corpus cutoff date and retrieval procedure.

### 8.3 Conceptual-Space Representation
Represent known ideas using:

- embeddings;
- structured attributes;
- graph relationships;
- task-specific features;
- optionally clustering/manifold representations.

We are interested in identifying:

- dense regions;
- sparse regions;
- disconnected/weakly connected regions;
- unexplored combinations of dimensions.

### 8.4 Exploration Agents
At minimum implement separate strategies:

1. Standard generator.
2. Contrarian generator.
3. Cross-domain recombination agent.
4. Assumption inversion agent.
5. Mutation/evolution agent.
6. Sparse-region targeting agent.

### 8.5 Quality-Diversity Archive
Candidate archive dimensions may include:

- mechanism class;
- algorithmic strategy;
- domain;
- complexity profile;
- semantic distance;
- behavior/features.

Preserve diverse high-quality candidates instead of keeping only the top score.

### 8.6 Novelty Verification
Use multiple independent signals:

- lexical similarity;
- dense retrieval;
- embedding similarity;
- structured/facet similarity;
- graph similarity;
- prior-art LLM analysis;
- adversarial search;
- human review for final evaluation.

### 8.7 Objective Evaluator
The evaluator must be as deterministic as possible.

Examples:

- benchmark score;
- runtime;
- memory;
- correctness;
- test-suite pass rate;
- objective-function value;
- complexity penalty.

### 8.8 Experiment Controller
Tracks every generation and prevents:

- duplicate ideas;
- accidental data leakage;
- evaluator cheating;
- uncontrolled prompt changes;
- unverifiable experimental claims.

---

## 9. The Most Important Metric

Define:

```text
Novel-Success Rate =
    Number of candidates that are
    (1) sufficiently novel under the frozen novelty protocol
    AND
    (2) objectively successful
    ----------------------------------------------------------
    Total number of generated candidates
```

Secondary metrics:

- novelty score;
- semantic distance from prior art;
- diversity;
- quality;
- feasibility;
- expert-rated originality;
- expert-rated surprise;
- prior-art retrieval rate;
- false-novelty rate;
- compute cost per successful discovery;
- generations per successful discovery;
- evaluator pass rate.

Do not optimize solely for novelty. The system can cheat by becoming useless.

---

## 10. Required Baselines

At minimum:

**B0 — Random / trivial baseline**  
Useful only as a sanity check.

**B1 — Vanilla LLM**  
Independent idea generation with a fixed prompt.

**B2 — Reasoning LLM**  
Same task with a reasoning-capable model.

**B3 — RAG researcher**  
Retrieve relevant material and generate ideas.

**B4 — Iterative ideation baseline**  
Generate → critique → refine.

**B5 — Evolutionary LLM baseline**  
Mutation/evolution without explicit sparse-region exploration.

**B6 — Quality-only search**  
Optimize task performance while ignoring novelty.

**B7 — Quality-diversity without sparse-space targeting**  
Tests whether MAP-Elites/QD alone explains gains.

**B8 — OPENEND full system**  
Sparse-space targeting + QD + structured exploration + adversarial novelty verification + objective evaluation.

Exact models must be recorded by model identifier/version/date.

---

## 11. Required Ablation Studies

Remove one major component at a time:

1. No sparse-region targeting.
2. No novelty objective.
3. No quality-diversity archive.
4. No structured mutation.
5. No cross-domain recombination.
6. No adversarial novelty verifier.
7. No external prior-art search.
8. No objective evaluator.
9. No iterative feedback.
10. Single-agent instead of multi-agent.

Also test combinations where scientifically meaningful.

The final paper must show whether the proposed mechanism actually matters.

---

## 12. Benchmark Design

We need two evaluation regimes.

### Regime A — Historical / frozen-corpus benchmark

Use problems whose relevant prior solutions are known up to a cutoff date.

The system cannot access post-cutoff knowledge during generation.

Question:

> Can it independently rediscover or extend useful solutions without directly retrieving the target solution?

### Regime B — Discovery benchmark

Use open-ended problems where multiple valid solutions exist.

Candidates are evaluated by objective tests.

Question:

> Does the system generate useful solutions that are substantially different from known references?

### Leakage test

Before experimentation, audit prompts, retrieval corpora, benchmarks, model documentation, and test suites for direct leakage of the target solution.

---

## 13. Experimental Protocol

Every experiment must log:

```text
run_id
time
code_commit
config_hash
model_name
model_version
provider
prompt_version
corpus_version
corpus_cutoff
random_seed
candidate_id
parent_ids
generation
retrieved_documents
novelty_scores
prior_art_hits
objective_score
runtime
memory
final_status
```

All runs should be reproducible as far as API/model nondeterminism permits.

Never manually remove failures from the dataset after seeing results.

Define inclusion/exclusion rules before final analysis.

---

## 14. Research Reproducibility Rules

1. Version control everything.
2. Pin Python dependencies.
3. Store model identifiers and provider versions.
4. Freeze prompts before final experiments.
5. Store benchmark versions.
6. Store dataset hashes.
7. Keep raw logs immutable.
8. Separate development from held-out evaluation.
9. Never use held-out answers in prompt engineering.
10. Record API costs.
11. Record failed runs.
12. Run multiple random seeds where feasible.
13. Report compute budget.
14. Report model access limitations.
15. Never silently change the evaluator after seeing results.

---

## 15. Human Evaluation

Human experts should be used only after automated filtering has narrowed the candidate set.

Evaluation dimensions:

- novelty/originality;
- usefulness;
- feasibility;
- technical soundness;
- surprise/unexpectedness;
- prior-art familiarity;
- overall research value.

Important:

- blind the origin of each idea;
- randomize presentation order;
- include human-authored/reference ideas where appropriate;
- include baseline LLM ideas;
- use multiple raters;
- report inter-rater agreement;
- define rating instructions before the study;
- obtain appropriate institutional ethics/IRB review if required by the institution and jurisdiction.

Human evaluation should test expert judgment, not serve as the only evidence of novelty.

---

## 16. Adversarial Novelty Evaluation

For every high-scoring candidate, create an independent novelty-verification pipeline.

Agent A:

> Argue that this idea is novel.

Agent B:

> Search for the closest prior art and equivalent concepts.

Agent C:

> Search for indirect conceptual equivalents and different terminology.

Agent D:

> Try to falsify the novelty claim.

Human expert:

> Review the evidence for the final benchmark subset.

The final novelty score must consider contradictory evidence.

---

## 17. Anti-Cheating / Failure Modes to Test

The agent may attempt to maximize the wrong metric.

Test explicitly for:

### Novelty hacking
Creating absurd or meaningless ideas that are far from existing work.

### Obscure wording
Changing language while keeping the underlying idea identical.

### Combination laundering
Combining two known ideas and claiming the combination is new without meaningful innovation.

### Retrieval leakage
Generating a known answer after indirectly retrieving it.

### Evaluator gaming
Finding loopholes in the benchmark rather than solving the intended task.

### Diversity theater
Generating many surface variants of the same underlying idea.

### Judge gaming
Producing text that persuades the LLM novelty evaluator without being substantively novel.

The system must be tested specifically against these failure modes.

---

## 18. Required Research Artifacts

The final project should contain:

1. Research paper.
2. Source code.
3. Configuration files.
4. Benchmark definition.
5. Frozen evaluation corpus metadata.
6. Dataset generation scripts.
7. Experiment runner.
8. Raw experiment logs where legally shareable.
9. Evaluation scripts.
10. Analysis notebooks/scripts.
11. Figures and tables generated from code.
12. Reproducibility instructions.
13. Model/prompt configuration history.
14. Limitation and failure-case dataset.
15. Example discovery trajectories.

---

## 19. Repository Structure

```text
OPENEND/
│
├── README.md
├── LICENSE
├── CITATION.cff
├── pyproject.toml
├── requirements.lock
│
├── docs/
│   ├── research-question.md
│   ├── literature-map.md
│   ├── hypotheses.md
│   ├── experimental-protocol.md
│   ├── ethics.md
│   └── publication-plan.md
│
├── paper/
│   ├── main.tex
│   ├── references.bib
│   ├── figures/
│   ├── tables/
│   └── appendix/
│
├── configs/
│   ├── baseline.yaml
│   ├── qd.yaml
│   ├── exploration.yaml
│   └── full_openend.yaml
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── corpus_manifest/
│   └── benchmark/
│
├── src/
│   ├── agents/
│   ├── representation/
│   ├── exploration/
│   ├── qd/
│   ├── evolution/
│   ├── retrieval/
│   ├── novelty/
│   ├── evaluation/
│   ├── orchestration/
│   └── logging/
│
├── experiments/
│   ├── baselines/
│   ├── ablations/
│   ├── scaling/
│   ├── human_eval/
│   └── adversarial/
│
├── analysis/
│   ├── metrics/
│   ├── statistics/
│   └── plots/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── regression/
│
└── results/
    ├── raw/
    ├── processed/
    ├── tables/
    └── figures/
```

---

## 20. Development Roadmap

### PHASE 0 — Research lock

Tasks:

- finalize research question;
- finalize hypotheses;
- define operational novelty;
- define first domain;
- define benchmark families;
- decide first model set;
- define metrics;
- define stopping/selection rules;
- create research log.

**Gate:** We can state exactly what experiment could falsify the thesis.

### PHASE 1 — Literature + gap validation

Tasks:

- create bibliography;
- read strongest 20–30 papers;
- map their methods and limitations;
- reproduce claims relevant to our gap;
- document what has already been attempted;
- identify exact novelty relative to each closest paper.

**Gate:** We can explain why OPENEND is not merely FunSearch, AlphaEvolve, NOVA, AI Scientist, Co-Scientist, or MAP-Elites with an LLM attached.

### PHASE 2 — Benchmark construction

Tasks:

- select task families;
- collect reference solutions;
- define objective evaluators;
- create frozen corpus;
- establish leakage controls;
- create benchmark runner;
- validate benchmark independently.

**Gate:** Every candidate can be scored automatically without human intervention for the first benchmark.

### PHASE 3 — Baselines

Implement B0–B7 before the full system.

**Gate:** Baselines run end-to-end and generate comparable logs.

### PHASE 4 — OPENEND v0

Build the smallest viable loop:

```text
problem
→ generate candidates
→ embed/represent
→ sparse-region score
→ mutate/recombine
→ objective evaluation
→ archive
→ repeat
```

No complex multi-agent system yet.

**Gate:** It produces measurable diversity and objective performance.

### PHASE 5 — Novelty verification

Add:

- retrieval;
- semantic similarity;
- prior-art evidence;
- adversarial verifier;
- novelty report.

**Gate:** We can detect known solutions and false-novelty cases reliably.

### PHASE 6 — Full OPENEND

Combine:

- multi-agent generation;
- conceptual-space exploration;
- quality-diversity archive;
- structured mutation;
- adversarial novelty verification;
- executable evaluation.

**Gate:** Full pipeline is reproducible from one experiment command.

### PHASE 7 — Controlled experiments

Run:

- all baselines;
- full system;
- ablations;
- multiple seeds;
- compute-budget matched comparisons;
- model comparisons.

**Gate:** Locked statistical analysis dataset.

### PHASE 8 — Red team

Try to break the scientific claim.

Search specifically for:

- leakage;
- duplicate ideas;
- false novelty;
- benchmark gaming;
- evaluation artifacts;
- prompt sensitivity;
- model-version sensitivity.

**Gate:** Every discovered weakness is either fixed or explicitly reported.

### PHASE 9 — Human evaluation

Run blinded expert evaluation on a preregistered/frozen candidate subset where feasible.

**Gate:** Human study complete and raw data preserved.

### PHASE 10 — Final analysis

Generate all statistics and figures from scripts.

Primary result should be decided before looking at secondary analyses whenever practical.

**Gate:** We can answer every RQ with evidence.

### PHASE 11 — Paper writing

Write only after experimental evidence stabilizes.

Paper structure:

1. Abstract
2. Introduction
3. Problem Definition
4. Related Work
5. Method
6. Novelty Representation
7. Search / QD Algorithm
8. Novelty Verification
9. Experimental Setup
10. Results
11. Ablations
12. Human Evaluation
13. Failure Cases
14. Limitations
15. Ethics / Broader Impact
16. Conclusion
17. References
18. Appendix

### PHASE 12 — Internal review

At least three independent reviews:

- ML reviewer;
- agent/autonomous-science reviewer;
- novelty/evaluation reviewer.

Each should attempt to reject the paper.

### PHASE 13 — Artifact/reproducibility audit

Check:

- clean environment installation;
- fresh-machine run;
- experiment reconstruction;
- figures rebuild;
- tables rebuild;
- random-seed behavior;
- model/API documentation;
- dataset licensing;
- third-party licenses.

### PHASE 14 — Preprint

After the work is mature and author/IP decisions are settled, prepare an arXiv-compatible version and repository release as appropriate.

Do not upload unfinished experimental claims merely to establish priority.

### PHASE 15 — Peer-reviewed publication

Prioritize venues based on the final contribution rather than forcing the project into a conference prematurely.

Potential classes of venue:

- top ML conference;
- AI/agent conference;
- computational creativity venue;
- autonomous-science/scientific-ML venue;
- evaluation/benchmark venue;
- journal.

At submission time, check that venue's then-current CFP, page limits, anonymity rules, AI-use policy, dual-submission rules, code/data requirements, and ethics requirements.

### PHASE 16 — Rebuttal / revision / camera-ready

Tasks:

- classify reviewer criticisms;
- run only pre-approved/additional experiments where needed;
- prepare evidence-backed rebuttal;
- avoid changing claims beyond evidence;
- update appendix;
- prepare camera-ready;
- archive exact accepted version and artifacts.

### PHASE 17 — Post-publication

Tasks:

- public repository;
- demo;
- benchmark release where legal;
- model/prompt configs;
- technical report;
- follow-up paper on broader domains;
- challenge/benchmark proposal if results justify it.

---

## 21. Immediate First Sprint

Do not start by building the complete architecture.

### Day 1

Create repository.

Create research log.

Create bibliography database.

Write exact hypotheses.

Choose first algorithmic benchmark domain.

### Day 2

Build corpus-ingestion prototype.

Define corpus cutoff.

Implement document/chunk metadata schema.

Implement embeddings and retrieval.

### Day 3

Implement baseline LLM generator.

Implement objective evaluator.

Store candidate trajectories.

### Day 4

Implement conceptual-space representation.

Implement density/sparsity estimation.

Visualize candidate space.

### Day 5

Implement novelty-targeted exploration.

Implement basic mutation/recombination.

### Day 6

Implement archive / quality-diversity mechanism.

Implement duplicate and semantic-near-duplicate detection.

### Day 7

Run first controlled comparison:

```text
Vanilla LLM
vs
RAG
vs
Novelty Search
vs
QD
vs
OPENEND-v0
```

At the end of the first sprint we should have **numbers**, not just a demo.

---

## 22. First Proof-of-Concept Success Criteria

The POC is successful only if it demonstrates at least one of these:

1. Higher novel-success rate than a strong baseline.
2. Higher novelty at matched utility.
3. Higher diversity at matched quality.
4. Discovery of an objectively better solution that the baselines did not produce.
5. Significant reduction in false novelty claims.

A visually impressive demo without a controlled baseline comparison is not sufficient evidence.

---

## 23. Paper Contribution Target

The final paper should aim for four contributions:

### Contribution 1 — Method
A principled architecture for open-ended conceptual/solution-space exploration.

### Contribution 2 — Algorithm
A concrete sparse-region + quality-diversity discovery mechanism.

### Contribution 3 — Evaluation
A multi-stage novelty verification protocol that is harder to game than single-model novelty judgment.

### Contribution 4 — Empirical evidence
Controlled evidence that the architecture increases the rate of useful, novel discoveries.

If the experiments do not support all four, reduce the claims rather than exaggerating.

---

## 24. What Would Count as a Strong Result?

Strong:

> OPENEND generates 2–3× more corpus-novel, benchmark-successful candidates than baseline at equal compute budget, while maintaining comparable feasibility.

Very strong:

> Experts blindly rate OPENEND candidates as substantially more surprising while objective evaluation shows equal or superior utility.

Exceptional:

> OPENEND discovers an algorithm/solution that is objectively superior to the strongest reference and absent from the frozen knowledge corpus, with independent prior-art analysis failing to identify an equivalent solution.

A weak result is still useful if it reveals a scientifically important failure mode. A negative result should be published honestly if the methodology is rigorous and the finding is meaningful.

---

## 25. Things We Must NOT Do

- Do not claim “AI invented something never seen by humanity” without overwhelming evidence.
- Do not use a single LLM judge as the only novelty evaluator.
- Do not evaluate on the same data used to tune prompts.
- Do not quietly inspect the target answer and then modify the system.
- Do not compare systems with wildly different compute budgets without reporting it.
- Do not report only successful runs.
- Do not remove failed discoveries from qualitative examples.
- Do not call surface-level paraphrasing an invention.
- Do not present an engineering demo as scientific evidence.
- Do not submit before the experimental protocol and claims are mature.

---

## 26. Current Research Position

The project begins from the following evidence-backed position:

- Novelty Search shows that novelty can be an explicit exploration objective.
- MAP-Elites shows that quality and diversity can be maintained simultaneously.
- FunSearch and AlphaEvolve show that LLM-guided evolutionary search can discover useful algorithmic solutions.
- AI Scientist / Co-Scientist / Robin show increasingly autonomous research loops.
- NOVA and related work show that iterative, search-aware ideation can improve novelty.
- Recent novelty-evaluation work shows that LLM judgments of novelty can be unreliable.

Therefore, the project hypothesis is that **explicit exploration of sparse conceptual regions + quality-diversity preservation + adversarial novelty verification + objective validation** may be a useful missing layer between “creative LLM” and “reliable autonomous discovery.”

This is a hypothesis to test, not an established fact.

---

## 27. Research Discipline

For every major claim, maintain:

```text
Claim
→ Evidence
→ Experiment
→ Metric
→ Result
→ Limitation
```

For every result, maintain:

```text
Result
→ code commit
→ config
→ model/version
→ dataset/corpus hash
→ seed
→ raw logs
```

For every purported discovery, maintain:

```text
Candidate
→ generation history
→ prior-art evidence
→ novelty verdict
→ objective test
→ independent reproduction
```

---

## 28. Current Priority Order

Do these in order:

1. Lock research question.
2. Lock operational definitions.
3. Lock benchmark domain.
4. Build frozen corpus and leakage protocol.
5. Implement baseline generators.
6. Implement objective evaluator.
7. Implement conceptual-space representation.
8. Implement sparse-region exploration.
9. Implement quality-diversity archive.
10. Implement adversarial novelty verification.
11. Run controlled experiments.
12. Run ablations.
13. Red-team the results.
14. Run human evaluation.
15. Freeze analysis dataset.
16. Write paper from results.
17. Internal peer review.
18. Reproducibility audit.
19. Preprint when mature.
20. Submit to the best-fit peer-reviewed venue at the applicable future deadline.

---

## 29. Useful Research References

The following are starting points, not the complete bibliography.

- FunSearch: https://www.nature.com/articles/s41586-023-06924-6
- AlphaEvolve: https://arxiv.org/abs/2506.13131
- The AI Scientist: https://arxiv.org/abs/2408.06292
- Co-Scientist: https://doi.org/10.1038/s41586-026-10644-y
- Robin: https://doi.org/10.1038/s41586-026-10652-y
- Novelty Search: https://pubmed.ncbi.nlm.nih.gov/20868264/
- MAP-Elites: https://arxiv.org/abs/1504.04909
- NOVA: https://arxiv.org/abs/2410.14255
- Literature-Grounded Novelty Assessment: https://aclanthology.org/2025.sdp-1.9/
- LiveIdeaBench: https://www.nature.com/articles/s41467-026-70245-1
- RQ-Bench / novelty mirage: https://arxiv.org/abs/2606.12071
- Structured Recombination / creativity: https://aclanthology.org/2026.tacl-1.20/

---

## 30. Publication Strategy Notes (Current as of 2026-10-07)

Do not anchor the project to a closed deadline.

Current known timelines show that ICLR 2027's paper deadline was September 25, 2026, and AAAI-27's main technical full-paper deadline was July 28, 2026. Therefore those main submission windows are already closed as of this project's start date.

Target selection should occur after the evidence is mature. Potential targets include a future major ML conference, a suitable AI/agent/autonomous-discovery venue, an evaluation/benchmark venue, a workshop, or a journal.

At the actual submission date, read the current venue's official policies rather than relying on this file for deadlines.

---

## 31. Definition of Done

The project is not “done” when the agent generates interesting ideas.

It is done when we can reproduceably answer:

> **Does deliberate exploration of sparse conceptual regions produce a statistically and practically meaningful increase in validated novel-success discoveries compared with strong, compute-matched baselines?**

And we can provide the code, protocol, data provenance, analysis, limitations, and evidence required for an independent researcher to audit the claim.

---

# END OF PROJECT CONTEXT
