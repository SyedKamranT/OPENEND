> **Active local refinement (2026-10-10):** Phase 1 remains OPEN. Use docs/research-log.md and docs/refined-pilot-protocol.md for the current local-only continuation. configs/local_refined_pilot.json governs the refined Qwen/Gemma development pilot. Historical cloud attempts are preserved but are not the active workflow.

> **Active amendment ? 2026-10-08:** Phase 1 has been reopened following `docs/research-review-2026-10-08.md`. Current decisions are in `docs/research-question.md` and `docs/experimental-protocol.md`; `configs/pilot.json` governs the implemented bounded bin-packing comparison. Phase numbering in `phases.md` is canonical. The original planning text below is historical intent, not evidence of completed features or a scientific lock. A fixed 2024 cutoff, zero-leakage guarantees, model choices, old seed/budget values, and venue timelines are not active pilot commitments.

Yes. We should treat this as a **real research + engineering program**, with the paper as the final output of the experiments—not as a document we write first and then try to justify.

I created the IDE context file containing the research objective, hypotheses, architecture, benchmarks, baselines, experiments, ablations, novelty verification, reproducibility rules, human evaluation, publication workflow, repository structure, and a first-week execution plan:

:chatgpt-content-reference{index="2"}[Download OPENEND_PROJECT_CONTEXT.md](sandbox:/mnt/data/OPENEND_PROJECT_CONTEXT.md)

## The project we are officially pursuing

### Working name
**OPENEND — Open-Ended Novelty Discovery Agent**

### Core research question

> Can an AI agent deliberately explore underrepresented regions of conceptual/solution space and discover useful ideas that are novel relative to a frozen knowledge corpus and difficult for standard LLM/RAG systems to produce?

The important thing is that we are **not** claiming to build an AI that magically invents anything from nothing.

We're testing whether we can engineer a system where:

**exploration → diversity → novelty verification → objective validation**

becomes a deliberate discovery process.

---

# Exact execution order

### Phase 1 — Research lock

We first freeze:

1. Research question
2. 4–6 hypotheses
3. Operational definition of novelty
4. First research domain
5. Evaluation metrics
6. Baselines
7. Experimental protocol
8. Leakage rules
9. Success/failure criteria

**Deliverable:** `research-question.md`

---

### Phase 2 — Literature and gap validation

We create a structured literature database around:

- Novelty Search
- MAP-Elites / Quality-Diversity
- FunSearch
- AlphaEvolve
- AI Scientist
- NOVA
- Co-Scientist
- Robin
- scientific idea-generation systems
- novelty verification
- divergent-thinking benchmarks
- structured recombination
- autonomous discovery

Then we create a matrix:

| Paper | Generation | Search | Diversity | Novelty verification | Objective validation | Sparse-space exploration |
|---|---:|---:|---:|---:|---:|---:|
| FunSearch | ✓ | ✓ | partial | — | ✓ | — |
| AlphaEvolve | ✓ | ✓ | partial | — | ✓ | — |
| NOVA | ✓ | ✓ | partial | partial | — | — |
| Co-Scientist | ✓ | ✓ | ✓ | partial | ✓ | — |
| OPENEND | ✓ | ✓ | ✓ | ✓ | ✓ | **✓** |

The point is to make our claimed contribution **defensible against the closest existing work**.

---

# Phase 3 — Build the benchmark first

This is extremely important.

We should **not build the fancy agent first**.

We build the evaluator first.

Our initial domain will be:

> **algorithmic/software invention**

because we can automatically test whether a proposed solution actually works.

For each task we need:

```text
problem
known solutions
objective
constraints
test cases
evaluation function
reference scores
novelty corpus
```

Then we can objectively answer:

> Did the generated idea work?

rather than asking an LLM whether it "looks innovative."

---

# Phase 4 — Implement baselines

Before OPENEND exists, implement:

```text
B0 Random
B1 Vanilla LLM
B2 Reasoning LLM
B3 RAG Researcher
B4 Generate → Critique → Refine
B5 Evolutionary LLM
B6 Quality-only search
B7 Quality-Diversity
B8 OPENEND
```

Every system gets approximately comparable compute budgets.

This prevents us from accidentally building a complicated system that only wins because it spent 50× more inference calls.

---

# Phase 5 — Build OPENEND v0

The first version will be deliberately simple:

```text
Problem
   ↓
Generate candidate ideas
   ↓
Represent ideas in conceptual space
   ↓
Estimate density / similarity
   ↓
Target sparse regions
   ↓
Mutate / recombine
   ↓
Evaluate objectively
   ↓
Keep diverse high-quality candidates
   ↓
Repeat
```

At this point we **do not need 15 agents**.

We need to demonstrate that the mechanism itself works.

---

# Phase 6 — Add the novelty system

Then build the serious novelty layer.

For every candidate:

```text
Candidate
   ↓
Semantic retrieval
   ↓
Literature search
   ↓
Patent search
   ↓
Code / solution search
   ↓
Conceptual similarity
   ↓
Adversarial search
   ↓
Novelty verdict
```

And we explicitly test the failure case:

> "This looked novel to the LLM, but an expert found it was already known."

This is important because recent research has shown a **novelty-mirage problem** in LLM-based evaluation.

---

# Phase 7 — Add evolutionary discovery

Now candidates become actual evolving objects.

For example:

```text
Idea A
 ├── mutate mechanism
 ├── invert assumption
 ├── change constraint
 ├── cross with Idea B
 ├── transfer from another domain
 └── simplify
```

This is where OPENEND begins becoming materially different from normal agentic prompting.

---

# Phase 8 — Quality-Diversity archive

Instead of:

> Keep the top 10 ideas.

we maintain:

> **The best ideas across many different regions of solution space.**

This is where the old Novelty Search / MAP-Elites literature becomes particularly valuable.

The system shouldn't converge immediately on:

```text
best_known_solution
best_known_solution+
best_known_solution++
```

It should retain:

```text
Region A → excellent solution
Region B → unusual solution
Region C → strange but promising solution
Region D → cross-domain solution
Region E → radically different mechanism
```

Then each region can continue evolving.

---

# Phase 9 — The key metric

We will make this one of the central measurements:

### Novel-Success Rate

```text
validated novel + successful candidates
----------------------------------------
all generated candidates
```

Because:

**Novelty alone is easy.**

Generate nonsense.

**Utility alone is easy.**

Rediscover known solutions.

The interesting intersection is:

> **Novel + useful**

---

# Phase 10 — Ablations

We remove components one by one:

```text
without sparse-space exploration
without QD
without evolutionary mutation
without cross-domain recombination
without novelty verifier
without adversarial search
without RAG
without multi-agent system
```

This tells us **what actually caused the improvement**.

Without ablations, reviewers can legitimately say:

> "Maybe the LLM was just stronger."

---

# Phase 11 — Red-team the research

Before we celebrate any result, we try to destroy it.

We actively test:

### Novelty hacking
Generate useless ideas that are extremely distant from known work.

### Wording hacking
Change terminology without changing the underlying idea.

### Combination laundering
Combine two existing ideas and claim invention.

### Retrieval leakage
Accidentally retrieve the answer.

### Benchmark gaming
Exploit the evaluator instead of solving the intended problem.

### Judge gaming
Generate text that convinces the novelty judge.

### Diversity theater
Produce 100 superficial variants of the same idea.

A strong paper should contain these failure cases.

---

# Phase 12 — Human study

Only after automated filtering.

Experts see blinded:

```text
Human idea
Baseline LLM idea
RAG idea
Evolutionary idea
OPENEND idea
```

They score:

- originality
- surprise
- feasibility
- usefulness
- technical quality

We then measure inter-rater agreement and compare systems.

Because recent research shows that **LLM-rated novelty and expert-rated novelty can diverge substantially**, human validation is important for the stronger claims.

---

# Phase 13 — Final experiments

Then we run the complete matrix:

```text
Baselines
×
Models
×
Tasks
×
Seeds
×
Ablations
×
Compute budgets
```

Everything gets logged.

No manual result selection.

No deleting failed runs.

No changing the evaluator after seeing results.

---

# Phase 14 — Freeze the evidence

Before writing the final paper:

```text
code commit
dataset version
corpus snapshot
model versions
prompt versions
experiment configs
raw logs
evaluation results
statistics
figures
```

are frozen.

Then the analysis is produced programmatically.

---

# Phase 15 — Write the paper

Only now.

Proposed structure:

```text
1. Abstract
2. Introduction
3. Problem Definition
4. Related Work
5. Method
6. Conceptual-Space Representation
7. Sparse-Region Exploration
8. Quality-Diversity Search
9. Novelty Verification
10. Experimental Setup
11. Results
12. Ablations
13. Human Evaluation
14. Failure Cases
15. Limitations
16. Ethics / Broader Impact
17. Conclusion
```

The paper's central claim should be whatever the experiments actually establish—not whatever we hope they establish.

---

# Phase 16 — Internal peer review

We should simulate hostile peer review.

Three independent perspectives:

**Reviewer A:** ML / optimization

**Reviewer B:** agents / autonomous science

**Reviewer C:** novelty / creativity / evaluation

Each gets one instruction:

> **Try to reject this paper.**

Then we repair the weaknesses.

---

# Phase 17 — Reproducibility audit

A clean machine should be able to:

```text
clone repository
↓
install dependencies
↓
download permitted data
↓
run benchmark
↓
run experiments
↓
generate tables
↓
generate figures
```

without undocumented manual steps.

---

# Phase 18 — Publication

As of **October 7, 2026**, we should not rush this into a closed conference deadline.

ICLR 2027's paper deadline was September 25, 2026, and AAAI-27's main technical deadline was July 28, 2026. NeurIPS 2026's main-track deadline was May 6, 2026. [ICLR](https://www.iclr.cc/Conferences/2027/CallForPapers?utm_source=chatgpt.com)

So our strategy is:

**Build strong research → preprint when mature → target the next appropriate major venue/workshop/journal.**

Venue selection should happen after we know the actual contribution.

---

# The first concrete milestone

Our **first milestone is not “build the AI inventor.”**

It is:

> ### **Build a reproducible benchmark where we can determine whether an idea is simultaneously novel, diverse, and objectively successful.**

Once that evaluator exists, building agents becomes meaningful.

Our first experiment should eventually look like:

```text
             SAME PROBLEMS
                   │
       ┌───────────┼────────────┐
       ↓           ↓            ↓
   Vanilla       RAG        Evolution
       │           │            │
       └───────────┼────────────┘
                   ↓
              OPENEND-v0
                   │
                   ↓
       ┌───────────────────────┐
       │ novelty + diversity   │
       │ utility + feasibility │
       └───────────────────────┘
                   │
                   ↓
          statistical comparison
```

And the paper ultimately needs to answer one question:

> **Does deliberately searching underrepresented conceptual regions produce more validated novel-success discoveries than strong conventional AI research agents?**

That is the experiment we're building toward.

C:\Users\unity\Downloads\OPENEND\OPENEND_PROJECT_CONTEXT.md