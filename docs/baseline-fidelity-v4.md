# Baseline numerical fidelity and integration audit v4

2026-10-16. Internal technical review; no independent-review claim.

## Probability audit

Executed the hash-pinned FunSearch `_softmax` and `Cluster.sample_program` functions
using actual NumPy 1.26.4 / SciPy 1.14.1. No whole upstream module or generated program
was executed. Saved 48 probability fixtures (three dtypes, four score vectors, four
registration counts) and five program-length fixtures. Every length-probability fixture
agrees within 1e-12. Maximum probability difference from the local scalar implementation
is 0.00004528533346854916 over these fixtures. This is finite coverage, not distribution
identity. Upstream float32 conversion and rounding correction remain explicit differences.
Python and NumPy RNG streams are not equivalent merely because probabilities are close.

A separate objective-scale witness is materially larger. For totals [-1476,-1475,-1474]
at temperature .1, the best cluster probability is .999954600070331. Negative mean bins
on 48 streams gives .40466547299926836 at the same temperature. Multiplying the total-score
temperature by 48 reproduces the mean-score probabilities within floating tolerance.
This demonstrates scale sensitivity, not a prescribed native mapping for all objectives.
Do not silently rescale historical runs or call the current aggregate-score adapter native.

Artifacts: `results/raw/baseline-probability-audit-v1`, including source snapshots,
versions, all numerical arrays and hashes. Current implementation reproduces the report
exactly. Existing v1/v2/v3 source and evaluator findings remain part of the fidelity map.

## Live engineering attempt

The [prospective v2 protocol](phase4-engineering-v2-protocol.md) fixed 72 local calls.
The process was no longer running when inspected after continuation. The journal contains
31 started requests, 30 saved responses, and one unresolved request with unknown actual
usage. The cause of interruption is not established. No silent retry or run extension.

EoH completed 24 calls: 20 valid, four incomplete responses, 16065 accounted tokens.
The selected policy remains Best Fit, 1476 training bins; no utility success. Independent
generation has six saved responses and one pending request; FunSearch did not start.
These are not comparable completed arms. `results/raw/phase4-engineering-v2-recovery`
replays the entire recorded prefix exactly and preserves the pending request. Original
run artifacts are unchanged, including their stale running manifest; recovery evidence
supersedes that manifest's liveness status without rewriting historical bytes.

## Complete deterministic integration check

Under a separate predeclared fixture protocol, all 72 deterministic responses completed
across the three adapters and replayed exactly, with zero model calls. Protocol override
support ensures the runner snapshots the actual run protocol instead of always copying
historical v1. The fixture covers initialization, operator cycling, resets, selection,
accounting and replay. It does not replace the interrupted live comparison or demonstrate
model proposal quality. Artifacts: `results/raw/phase4-engineering-fixture-v1`.

## Native execution prerequisite

Read-only environment checks found no Docker executable and no listed WSL distribution.
No verified generated-Python containment currently exists. Reviewed source extraction is
an audit technique, not a sandbox. Native representation, prompt/completion parsing and
contained evaluator execution therefore remain outstanding. Do not remove these locked
Phase 4 obligations or claim full phase closure from adapted integration success.
