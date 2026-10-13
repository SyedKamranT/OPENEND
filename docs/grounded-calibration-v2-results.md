# Grounded critic, target controllability and representation results

2026-10-13. All results are training-only development diagnostics. No superiority,
model-family generalization, full-grammar impossibility or novelty claim is supported.
[Prospective protocol](grounded-calibration-v2-protocol.md).

## Connected local calibration

`results/raw/grounded-qwen35-4b-v2`: nine of nine requests completed with accounted usage,
8,286 tokens and 68.922 request-wall seconds. All nine responses were executable/schema-valid.
Model: installed local Qwen 3.5 4B; unchanged backend decoding settings. The model was
unloaded after completion. No cloud requests or model downloads occurred.

| Separate gate | Successful / attempted | Criterion | Outcome |
|---|---:|---:|---|
| Grounded critic: all original and revision choice claims correct | 1/3 | 3/3 | Failed |
| Target-only generation: requested cell reached | 0/3 | 3/3 | Failed |
| Supplied-witness control: requested cell reached | 1/3 | 3/3 | Failed |

All three original-policy choice vectors were correct with supplied host traces. Two
revision choice vectors were wrong and rejected. Their actual revisions increased
training bin count by 74 and 11 respectively. The accepted positive-gap case preserved
training bin count (delta zero). None improved training bin counts. A correct critique
can therefore still be useless; the gate checks evidence, not improvement.

The target requests use three elementary development states, not the full 96-state
search panel. Even exposing a witness did not reliably produce the requested behavior.
The tested prompt/model combination is not ready for a larger directed-search trial.
This is not an estimate of the general capability of Qwen or all local models. Do not
repeat until positive or reinterpret schema compliance as target control.

Saved responses replayed all nine assessments with zero model calls; 11 manifest hash
checks passed (seven distinct files, with four checked in both input/output groups).
The protocol text, request plan, model identity, source snapshot, usage and journal are saved.
Startup first encountered sandbox socket denial, then a stopped Ollama service; both
occurred during the version probe before generation and before the run directory existed.
Starting the installed loopback service resolved startup. These were not hidden model retries.

## Representation diagnostic

`results/raw/representation-audit-v1`: exhaustively evaluated 1,053 leaves and
one-operator expressions on 48 training streams. There were 54 distinct full training
assignment-signature vectors. Independent references used 1,493 bins (first-fit),
1,476 (best-fit), and 1,567 (worst-fit).

Best single enumerated policy: 1,476 bins, tying best-fit. The deterministic tie-selected
expression is `max(fraction, -1)`, which reduces to fraction on feasible positive-item bins
and chooses the smallest feasible remaining space. Utility-screen successes: zero.
Even the non-deployable oracle choosing the best enumerated policy per stream used
1,476 bins. All 1,053 saved evaluations replayed exactly without model calls.

This rules out an improvement in the enumerated subset on these training streams. It
does not rule out deeper expressions, richer state features, other distributions or
better policies elsewhere. The full grammar remains uncharacterized. The next useful
representation diagnostic expands the search under a new fixed budget, rather than
mistaking shallow enumeration for a proof of impossibility.

The initial representation manifest omitted the shared verifier's empty `input_files`
field. Its original bytes are preserved in `run_manifest.initial.json`; the repaired
manifest records the repair and hashes that original. Candidate scores were not changed.

## Implementation and limits

`openend.evidence` produces executable traces, checks complete training packing
certificates and rejects unsupported behavioral claims. `coordinator-grounded-v2` sends
only verified feedback to recombination. Rejected criticism consumes its call/token
budget. It is available as `configs/coordinator_grounded_v2.json` but no larger v2
coordinator experiment was launched after these gate failures.

The earlier coordinator v1 run still replays all 24 saved role calls. Tests cover
independent reference agreement, no-feasible-bin handling, ties, malformed/false claims,
rejected-feedback isolation, separate gates and both coordinator/calibration replay.
Ground truth shares the policy scoring function; independent imperative reference
implementations provide checks on known-reference cases, not every possible expression.
Only fixed-state behavioral claims are checked; arbitrary global claims are excluded
from the v2 feedback schema.

Final verification: **78 tests passed**, Ruff passed, and Git diff whitespace checks passed.

The remaining baseline, retrieval, independent-review and confirmation work is specified
in the [research upgrade plan](research-upgrade-plan.md). Phase 1 remains open.
