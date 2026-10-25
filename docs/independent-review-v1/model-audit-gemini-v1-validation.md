# Gemini model audit: maintainer validation, 2026-10-13

The supplied `model-audit-gemini-v1.json` is preserved unchanged. Its SHA-256 is
`cb5af71d8a59e5304405c9b41ed8034de1d67534014104fd1b21fadd1fefbc8a`.
It is one external model audit, with human independence explicitly unattested.
The model designation is user-reported; provider metadata, exact prompts, source browsing
transcripts and the original response export were not included. Their absence limits
verification of the model identity and search procedure; it does not invalidate the
mechanical claims that can be checked directly.

The user reports that the maintainer key was inspected only after the audit file was
written. That timing is a declaration, not independently authenticated provenance.
Any subsequent review in that same conversation must disclose exposure to the key.

## Executable findings

`python -m openend.model_audit_validation results/raw/<unused-validation-directory>`
replays all 18 supplied traces and checks 5,050 feasible item/residual score states per
reference control at capacity 100. All five controls agree with the proposed reference
labels: cases 01/04 are First Fit, 03/05 Best Fit, and 06 Worst Fit. Each is independent
of bin index and has constant or strictly monotone scores; the host supplies earliest
ties and opens a new bin only when necessary. These checks cover the integer benchmark
contract, not arbitrary capacities where protected division can alter rankings.

The saved validation is `results/raw/model-audit-gemini-v1-validation/validation.json`.
This is **5/5 agreement on reference controls**, not 6/6 novelty accuracy. The key's
`threshold_training_witness` entry describes origin; it contains no ground-truth novelty
label. No accuracy denominator may silently treat it as one.

Case 02 remains **unresolved** for research claims. The exact-arithmetic expression is
`max(item² - gap, 0)`: if any feasible bin has positive score it chooses the smallest gap;
only when every feasible score is zero does it choose the earliest feasible bin. This is
a decision over all candidates, not a separate FF/BF decision for each bin.
The original and simplified expression need not execute identically in floating point:
the preserved training audit reports 1,475 versus 1,476 bins. The original float and
exact-rational implementations also have a differing trajectory despite equal totals.
See `../representation-v2-results.md` and the numerical artifacts it identifies.

## Source and retrieval findings

The cited [Johnson article](https://www.sciencedirect.com/science/article/pii/S0022000074800267)
is an identifiable primary source, and the [FunSearch paper](https://www.nature.com/articles/s41586-023-06924-6)
is relevant prior art. Resolving a citation is not verifying every statement attributed
to it. Direct DOI fetches failed in this environment; publisher search records resolved
the titles. Wikipedia links do not satisfy the primary-source requirement by themselves.

Case 02's search log records algebra and a corpus-note search, but no reproducible
external query strings, search dates, databases, inspected passages or coverage limits.
This does not support absence from classical literature. `search_complete: true` is a
model assertion, not an evidence gate. Preserve its original verdict, with the maintainer
acceptance decision recorded separately as unresolved.

The 12 queries have existing corpus IDs and the requested 8/4 split. Their judgments are
**single-model provisional labels**. No retrieval scoring was run on this new set, so a
second reviewer can still label it before outputs are exposed. Points needing review:

- Queries 01/02 may have additional relevant records: the Next Fit context record also
  describes FF/BF, and the BF note discusses negative-gap and fraction rankings.
- Query 05 conflates mutation and crossover: the ELM corpus note supports mutation,
  not every operator named in the query. Decide whether partial relevance counts.
- Query 08 specifically requests OR-library scoring; labeling the separate Weibull
  heuristic relevant requires an explicit graded-relevance rule or revision.
- Query 12's named method has no supplied source; establish whether it is a real,
  intentionally synthetic, or mistaken entity before using it as an absent-topic test.

These are flags for adjudication, not replacement ground-truth labels authored by the
maintainer. Freeze the final rubric, both independent label sets, disagreements and
accepted qrels before evaluating retrieval. Two independent expert reviews and Phase 1
closure remain pending. A model review can improve this packet without satisfying them.
