# OPENEND research specification

**Status: REOPENED / PROVISIONAL ? not a confirmatory research lock.**
Amended 2026-10-08 following the [research review](research-review-2026-10-08.md).
Canonical roadmap numbering follows [phases.md](../phases.md). This document and the executable pilot configuration supersede the earlier frozen claims.

## 1. Core Research Question

Under a fixed model and resource allowance, does sparse-region targeting increase independently verified, distinct corpus-novel successful solutions compared with otherwise matched quality-diversity search?

The first implemented comparison is narrower: does corpus-relative behavioral sparsity weighting of parent selection improve exploration or held-out utility in a bounded online bin-packing policy language? This is a pilot of a search mechanism, not a demonstration of unrestricted algorithm invention or indefinite open-endedness.

RQ1: Does sparse targeting change behavioral coverage? RQ2: What happens to utility at matched allowances? RQ3: Can independent prior-art checking reliably distinguish known mechanisms? RQ4: Does distinct validated discovery yield improve? RQ5: Do blinded experts find improvements meaningful? RQ6: Is any difference attributable to sparse targeting? RQ3?RQ5 require additional evidence beyond this pilot.

## 2. Five hypotheses

[Hypotheses H1?H5](hypotheses.md) separate primary discovery claims, exploratory diagnostics, and deferred studies. No hypothesis is recorded as supported by a scaffold test or a nonsignificant result.

## 3. Operational definitions

**Corpus-Novel:** no equivalent mechanism identified by a completed, specified independent evidence search within a versioned corpus. This is protocol-relative, not universal novelty. An incomplete search returns **unresolved**.

**Semantically Novel:** a representation-based exploratory label only; distance is not evidence of invention. The pilot uses behavioral decision signatures rather than semantic embeddings.

**Validated Novel-Success:** independent corpus-relative novelty plus valid execution and a predefined utility criterion. This verdict is unavailable until the independent novelty audit exists.

The implemented reference set contains first-fit, best-fit, and worst-fit policies and content hashes. It is explicitly not a comprehensive literature corpus. Exact matches are known-reference candidates; every other candidate remains unresolved. Behavioral equivalence on 32 probes neither proves global equivalence nor disproves algorithmic novelty. Syntax deduplication is reported as syntax deduplication, not mechanism deduplication.

The previous arbitrary 2024 cutoff is withdrawn for this pilot. A future historical experiment needs separately justified publication/version and model-training cutoff policies. The current literature review includes relevant work through the review date.

## 4. First domain

**Algorithmic and Programmatic Problem Solving**, initially online one-dimensional bin packing. See the [benchmark contract](benchmark-bin-packing.md).

Candidates are JSON expression trees that score feasible bins. Inputs are integer item sizes; candidates cannot reorder a stream or access future items. The host controls placement, feasibility, and ties. This bounded language deliberately limits expressivity to permit safe deterministic evaluation without executing model-authored Python.

## 5. Metrics

The eventual primary metric is distinct validated novel-success discoveries per fixed budget. Retain attempt-level **Novel-Success Rate** (NSR) as a companion metric, with a frozen candidate accounting policy. It remains `null` in this pilot because the required novelty labels do not exist.

Implemented measurements: validity, duplicate syntax rate, distinct probe signatures, archive coverage, normalized QD score, training-selected candidate utility on held-out instances, utility-success rate, and API token usage. NSR bounds are descriptive: known non-novel candidates contribute zero; unresolved successful attempts determine the upper bound. A zero denominator yields `null`.

## 6. Baselines and controlled contrast

Standard references: independently implemented first-fit, best-fit, worst-fit. Search arms: `sparse_off` and `sparse_on`, both with the same 6?6 archive, initial references, evaluator, mutation/prompt operator, candidate limits, corpus, and seeds. Only parent sampling weights differ. Uniform weights are 1; sparse weights are 0.05 plus mean distance to the nearest two reference signatures.

B0?B8 from the original roadmap remain future comparator categories. The pilot does not claim a faithful implementation of FunSearch, AlphaEvolve, EoH, or a complete OPENEND system. Broader and stronger method baselines remain required before a publication claim.

## 7. Experimental protocol

The authoritative executable allowances are [pilot.json](../configs/pilot.json) and the smaller [api_pilot.json](../configs/api_pilot.json). They use the same schema and apply symmetrically to both arms. See [experimental-protocol.md](experimental-protocol.md) for stopping, provenance, and held-out evaluation rules.

## 8. Leakage Rules

Generation receives the parent policy and training score, never held-out instances or held-out feedback. All generation ends before validation/test scoring begins. Development pilot split seeds are public and reproducible, so these splits are withheld from the generator, not cryptographically sealed against a researcher. Confirmatory work needs a fresh independently controlled holdout.

Model memory can include known algorithms regardless of retrieval restrictions. Lexical overlap is not a guarantee against contamination. No claim of zero leakage or independent historical rediscovery is made.

## 9. Success and Falsification Conditions

Pilot engineering success means correct reference behavior, independently checked packing certificates, deterministic offline replay, matched settings, complete failure accounting, and a usable paired report. It does not require a positive treatment effect.

The pilot utility screen requires at least 1% fewer total bins than the best aggregate reference on test, with no family more than 5% worse than that same reference. These provisional margins were chosen before interpreting pilot results and are not statistical significance criteria.

Confirmatory superiority, practical equivalence, negative evidence, and insufficient precision are different outcomes. Practical effect margins, sample-size justification, an independent novelty rubric, and a task-level inference plan remain open. Phase 1 can close only after these decisions and literature-gap validation are documented; p > 0.05 cannot close or falsify the project.
