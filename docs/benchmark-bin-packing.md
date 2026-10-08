# Online bin-packing pilot benchmark v1

**Purpose:** validate the evaluator and compare sparse parent sampling with uniform sampling inside the same QD search. It is a bounded policy-search benchmark, not a general code-invention benchmark.

## Task contract

Each stream has 60 integer items and bin capacity 100. Items must be placed in arrival order without reordering or lookahead. Every item is assigned exactly once to a contiguous nonnegative bin index; no bin may exceed capacity. Only the host can open a bin, and it does so when no existing bin fits. Existing-bin scores use earliest-bin tie breaking. This restriction excludes policies that deliberately open bins early.

Four equally represented synthetic distributions:

- Uniform: 60 independent sizes from 1 to 99.
- Bimodal: each item equally chooses sizes 20?35 or 65?80.
- Paired: 30 complementary pairs summing to 100, shuffled. The exact optimum is 30 bins, certified by the planted partition and volume lower bound.
- Triplets: 20 triples summing to 100, shuffled. The exact optimum is 20 bins by the same certificate.

The paired/triplet optimum is an offline optimum, not a guarantee that an online algorithm can attain it. For other streams, volume and count-of-items-over-half-capacity provide valid lower bounds, not certified optima. Training fitness is the mean lower-bound/bins ratio, bounded by 1. Objective utility reports actual bin counts as well as fitness.

Each split has 12 streams per distribution by default. Split seeds are 1729 (training), 2718 (validation), and 31415 (test), with disjoint family offsets. Materialized JSON carries content hashes. These public development distributions are not claimed to represent industrial workloads or the full bin-packing literature.

## Candidate language

A response contains exactly one JSON field, `expression`. An expression is a finite numeric constant in [-10,10], a feature name, or an operator array. Examples:

```json
{"expression": ["neg", "gap"]}
```

This example is best-fit, a known heuristic, not a discovery.

Features are normalized residual gap, remaining capacity, current item size, bin position, item/remaining fraction, and exact-fit indicator. Binary operators: add, sub, mul, protected div, min, max. Unary operators: abs, neg. A tree has at most 31 nodes and depth 6 (root depth 0). Responses are limited to 16,384 UTF-8 bytes. Division by a denominator with magnitude below 1e-6 returns zero; each operator result is clipped to ?1e6. Booleans, nonfinite numbers, unknown keys/operators, duplicate JSON keys, and executable code are rejected.

## Independent checks and references

First-fit, best-fit, and worst-fit have separate imperative implementations for reference scoring. Expression-language versions initialize the search. Tests compare both implementations exhaustively over small streams and use a brute-force optimum oracle for additional correctness checks. A separate packing-certificate checker enforces completeness, capacity, and valid bin indices. Prefix tests confirm that future items cannot change earlier decisions.

The search maximizes training fitness. The training-selected generated candidate is evaluated on validation and test after every search run is finished. Utility success means at least 1% lower aggregate test bin count than the best aggregate reference, with no distribution more than 5% worse than that reference. This is a pilot engineering threshold, not an established meaningful effect size or significance test.

## Scope limits

The candidate grammar, fixed reference corpus, and small behavioral probe panel constrain what can be explored. Probe mismatches are behavioral differences, not mechanism novelty; syntactic duplicates and probe-equivalent candidates are reported separately. The current implementation cannot assign a positive scientific-novelty verdict. Next benchmark versions need stronger evolved baselines, independent prior-art adjudication, broader instances, and a protected confirmatory split before discovery claims.

FunSearch and EoH already study bin-packing heuristic discovery; the task is chosen for verifiability, not because the domain is unexplored. [FunSearch](https://www.nature.com/articles/s41586-023-06924-6), [EoH](https://arxiv.org/abs/2401.02051)
