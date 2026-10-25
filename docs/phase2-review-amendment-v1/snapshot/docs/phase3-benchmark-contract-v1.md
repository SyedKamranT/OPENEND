# Phase 3 benchmark contract v1 — 2026-10-15

**Status: ACTIVE — contract specified, acceptance work in progress.**
This captures the existing development behavior; it changes neither the search panel nor
historical experiments. [Phase 2 technical review](phase2-technical-review-2026-10-15.md)
provides the corrected handoff. Native baseline evaluators remain separate contracts.

## Task and host semantics

The current generator uses positive integer items and capacity 100, sixty arrivals per
stream and four families (uniform, bimodal, paired, triplets). `Instance` additionally
accepts capacities 1–10000 and at most 1000 items; this implementation range is not a claim
that all such distributions were evaluated. Items arrive in order; decisions cannot use
future items. Only feasible opened bins are scored. If none fits, open the next bin.
Maximize the score with earliest-bin tie breaking. Exact fits are feasible.

An independent certificate checks complete assignments, contiguous bin creation, valid
integer indices and capacity. Separate imperative First/Best/Worst Fit implementations
serve as references. Planted paired/triplet optima are generator properties; other counts
are lower bounds, not asserted optima. Keep construction evidence distinct from a solver
claim on arbitrary instances.

## Representation and numerical behavior

Policies are JSON expression data, never generated executable Python. The interpreter
allows at most 31 nodes, depth 6, finite constants in [-10,10], and 16384 response bytes.
The proposal protocol is narrower: four operator levels and constants
{-2,-1,-0.5,0,0.5,1,2}. Report which contract was used for every diagnostic candidate.

Features: gap=(space-item)/capacity; remaining=space/capacity; item=item/capacity;
index=bin_index/max(1,opened_bins-1); fraction=item/space; exact_fit=1 when space==item.
Operations use Python floating point; division returns zero when |denominator|<1e-6,
and operator outputs are clipped to [-1e6,1e6]. Algebraic rewrites are not presumed
bitwise equivalent. Retain exact-rational sensitivity results as a different evaluation.

## Objective, selection and interpretation

Optimize total training bins, including archive replacement via negative total bins.
The legacy mean(lower_bound/bins) remains historical and is not the active utility objective.
Select the earliest generated candidate with the lowest training count only if it strictly
beats the best training reference; otherwise retain that reference. Reference ties follow
recorded insertion order (First Fit, Best Fit, Worst Fit). Save the selected policy before
reading development evaluation outcomes.

Report total bins and per-family bins, paired uniform-minus-weighted differences and
equal-weight block summaries. The 1% improvement / maximum 5% family regression screen
uses the best aggregate reference; it is not a confirmatory between-arm margin. With
negative bin-count fitness, raw summed archive quality depends on occupancy and must not
be interpreted as a standalone utility improvement across differently filled archives.

## Search descriptor contract

The fixed legacy panel has 32 states with six bins each. Signatures are chosen bin indices;
distance is normalized Hamming disagreement. The weight is 0.05 plus the mean distance
to the two nearest of the three classical reference signatures, normalized over current
elites. Uniform uses equal elite weights. This is fixed-reference distance, not live
archive density, semantic novelty, prior-art absence or target reachability.

Descriptors average normalized residual gap and bin position, with a 6-by-6 archive in
the current protocol. The descriptor function requires a feasible existing bin in every
probe; host opening cases cannot be inserted into that panel without a versioned redesign.
Panel identity and limitations are recorded by the acceptance audit. Probe sensitivity
must be evaluated separately before robustness claims; it does not silently change search.

## Data and accounting contract

Use `development-blocks-v1` with seeds separated by version/master/block/role/family/index.
Roles are train and development_eval. Independent random seeds do not guarantee different
content; check and report duplicates for each frozen study. Existing old train/validation/test
splits and all public diagnostic data are development evidence. New same-family streams
measure within-generator generalization, not a distribution-shift claim or fresh confirmation.

Freeze all search and selection before evaluation. Preserve model identity, source/data
hashes, started/returned attempts, invalid outputs, actual known usage and unknown usage.
All arms use the same prospective allowances. Failed or interrupted runs are not silently
replaced. Final holdout and inference design belong to Phase 13.

## Acceptance ledger

| Requirement | Evidence/status |
|---|---|
| Host eligibility, opening and ties | Five explicit cases pass in `benchmark_acceptance.py` |
| Separate reference implementations | 816 comparisons pass; finite coverage, not a universal proof |
| Development stream identities | Sixteen fixture streams distinct; four dataset hashes saved |
| Probe limitations | Executable equality counterexample and category counts recorded |
| Selection and failure sequencing | Existing utility/block runner tests; full suite revalidated with this continuation |
| Numerical and representation boundaries | Existing interpreter tests and numerical audit; consolidate acceptance references before closure |
| Robustness / signal diagnosis | Pending: prospective diagnostic panel sensitivity and training-only useful-gain assessment |
| Frozen benchmark release bundle | Pending after remaining acceptance checks |

Reproduce the new checks with `python -m openend.benchmark_acceptance --output <new-report.json>`
from an environment with the package installed or `PYTHONPATH=src`. Output creation is
exclusive. No model backend is called. Phase 3 remains active until its remaining ledger
items are resolved and the release bundle is frozen; Phase 4 experiments follow it.

Validation this continuation: **130 tests passed in 41.60s; Ruff clean.** Evidence-level
counts, local links and diagnostic implementation hash verified. No new model calls.
