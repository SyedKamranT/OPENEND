# Matched proposal-operator comparison — 2026-10-25

Executed all 1024 attempts under the [predeclared development protocol](operator-comparison-v1-protocol.md).
Four fixed parents, 128 common seeds, two operators, unchanged finite grammar and
48 training streams. The baseline was previously inspected; this is adaptive development,
not a blinded confirmation. No model calls, holdout access or native execution.

| Measure | Subtree replacement | Single-token mutation |
|---|---:|---:|
| Charged attempts | 512 | 512 |
| Valid responses | 499 | 512 |
| Distinct valid policies | 228 | 82 |
| Syntax-identical parent copies | 14 | 0 |
| Training trajectory equal to parent | 101 | 93 |
| Best total bins | 1475 | 1475 |
| Proposals beating supplied 1475-bin incumbent | 0 | 0 |
| 1% / family screen passes | 0 | 0 |
| Beyond all parent distance thresholds on all four panels | 49 | 29 |
| Both useful-screen success and robust behavioral reach | 0 | 0 |

Single-token mutation improves validity and eliminates literal copies by construction,
but does not improve utility. Fewer distinct candidates is a material tradeoff. No
operator is promoted as a performance improvement. Finite training-trajectory agreement
is not universal semantic equivalence; probe distance is not scientific novelty.

## What the experiment changes in our diagnosis

The fixed proposal mechanisms can reach behavior beyond the supplied parents under
all four preselected reference-distance panels. Thus lack of any measurable behavioral
reach is not the explanation for the missing useful gain in this assay. It remains
unestablished whether a dynamic archive benefits from those proposals. The 49/29 counts
are attempts, not counts of distinct mechanisms or deployment probabilities.

A post-hoc exploratory candidate from subtree mutation, max(gap,fraction), uses 1476
bins and matches BF family totals (uniform 403, bimodal 406, paired 404, triplets 263).
It exceeds parent distance thresholds on all four panels: distances 0.5, 0.447917,
0.463542, 0.458333. It is a useful input for studying behaviorally different policies
without aggregate training degradation, but is neither a 1% improvement nor a novelty
claim. Three subtree attempts meet robust reach at or below BF total; zero single-token
attempts do. The best robust-reach single-token candidate uses 1482 bins.

The post-hoc candidate has 48 independently checked packing certificates saved in
`results/raw/operator-comparison-v1-posthoc`. Its selection was not the prospective
primary endpoint; any future use must disclose this training selection and seed it
identically in all compared arms. Do not treat its equal family totals as generalization.

## Decision for the central method

Do not simply strengthen distance weighting or replace the operator wholesale. Neither
has evidence of reaching the unchanged 1461-bin useful threshold. The current bottleneck
is obtaining useful change, not producing reference-distant behavior alone.

The next method-design hypothesis is to study a quality-constrained exploration pool:
retain behaviorally different, competitive policies and distinguish their expansion from
incumbent improvement. Test quality eligibility separately from distance weighting in a
matched factorial design; otherwise a gain could be incorrectly attributed to sparsity.
This is a proposed adaptation, not an originality claim or accepted replacement method.

Before another search experiment, write the representation/proposal diagnostic required
by this protocol: compare attainable candidate families, identify which useful decisions
need coordinated changes, and define training-only examples and stopping limits. Keep
the existing mutation/weighting baseline intact and predeclare all new seed information,
quality thresholds and costs. Useful signal and fresh evaluation are still required for
performance claims. Virtualization remains deferred by owner instruction.

Artifacts: `results/raw/operator-comparison-v1` includes every response, score, training
trajectory digest, panel reach, source archive and protocol. All 1024 attempts recomputed
exactly with canonical JSON normalization and every artifact hash verified.

Validation: full workspace suite **144 passed, 2 skipped** in 19.70s; Ruff clean.
The skips are optional NumPy/SciPy audit modules absent from the restored environment;
their six tests passed separately in the bundled numerical runtime earlier this day.
All 48 post-hoc candidate packing certificates were checked.
