# Fixed-parent opportunity results — 2026-10-25

Completed the [prospective assay](parent-opportunity-v1-protocol.md): 512 attempts,
499 valid responses, 228 distinct evaluated policies; no model calls, holdout access,
native code execution or dynamic archive search. Source/protocol/response artifacts:
`results/raw/parent-opportunity-v1`.

| Parent | Attempts | Valid | Distinct within parent | Better than parent | Better than BF | 1% screen |
|---|---:|---:|---:|---:|---:|---:|
| First Fit | 128 | 128 | 90 | 33 | 0 | 0 |
| Best Fit | 128 | 128 | 101 | 0 | 0 | 0 |
| Worst Fit | 128 | 128 | 90 | 101 | 0 | 0 |
| Historical witness | 128 | 115 | 107 | 0 | 2 | 0 |

The two 1475-bin responses came from the historical witness: seed 2026102601
returned the parent unchanged; seed 2026102563 replaced item with min(item,fraction).
On feasible capacity-bounded bins, fraction=item_size/remaining >= item_size/capacity,
so that minimum retains the item feature. This is preservation of the known mechanism,
not a newly improved policy or an independent novelty finding.

Uniform reference-relative expected gain was 0.00390625 bins per attempted proposal;
the weighted mixture gave 0.004193474264705882. The difference is driven solely by
assigning the supplied witness 26.838% rather than 25% probability. Best Fit receives
the same weight despite producing no better-than-BF offspring here. These quantities
are exact empirical mixtures for this fixed pool, not treatment effects in archive search.

Crucially, the predeclared incumbent was BF (1476), whereas the diagnostic pool already
contains a 1475-bin witness. Relative to the best supplied parent, every attempt has zero
retained gain. This additional interpretation is post-run and prevents calling witness
preservation discovery. The four-parent mixture is not the actual cell-collapsing archive.
No confidence interval, LLM generalization or mutation impossibility claim is made.

## Decision

Prioritize proposal/representation diagnosis before expanding model spending. This
bounded sample does not show that changing parent probabilities can produce a useful
online improvement. Preserve the weighting hypothesis as open; do not lower the screen.

Next predeclare a matched proposal-operator diagnostic: the current unconstrained subtree
mutation versus a structurally conservative operator, equal charged attempts, same fixed
parents and seeds, current finite grammar. The endpoint must improve the best supplied
parent, with copy/redundancy counts separate. This tests whether destructive proposals
are limiting progress before changing representation or launching native experiments.
Any later change to the experimental operator applies identically to both search arms,
gets a new protocol/version, and needs prospective development evaluation.

Validation: all 512 attempts reproduced exactly after canonical JSON normalization; artifact hashes verified. Restored locked Python 3.13 environment: 143 tests passed, two optional numerical-audit modules skipped (NumPy/SciPy unavailable); Ruff clean.

The six optional evaluator/probability tests also passed separately in the bundled NumPy/SciPy runtime (13.87s). The built-in LaTeX compilation request did not return; manuscript source was updated but PDF compilation is unverified.
