# Total-bin utility runner: offline engineering protocol v1

2026-10-14. Fixed before execution. Training-only engineering, not confirmation.

Run three paired seeds (42, 137, 2024), forty attempts per arm, on the existing 48
training streams. Arm names are uniform and reference_weighted. Use legacy 32-state
probes and six-by-six archive in both arms. Only parent sampling weights differ.
Archive quality is negative total bins; prompt feedback and final selection use total
bins. Strict improvement over the training-best reference is required to avoid fallback.
Earliest valid candidate wins generated ties; original valid ordinal is recorded alongside
the attempt index. All invalid proposals still consume attempts. Reference ties retain
the fixed reference insertion order. No critic, retrieval or explicit-target role.

The offline backend mutates the supplied parent with request seeds; it is not an LLM.
No provider tokens are consumed. The runner retains 60,000-token/512-output-cap fields
for its backend interface, with explicit zero offline reservations. Model-backed budget
tests use scripted usage, not provider calls. There is no live-model command in this version.

Use the finite four-level expression grammar for response acceptance in every backend;
offline out-of-grammar mutations are invalid attempts, never silently repaired. The host
interpreter retains its broader validation separately. Keep model prompts free of arm
labels and sampling probabilities. Record those in the journal for audit.

Journal started requests before dispatch, then processed responses, selection probabilities,
training scores and full archive state. Missing usage, model changes, overrun, API errors
and unexpected provider statuses stop the whole study. Truncation/invalid output remain
charged attempts. Unknown use is reserved but not represented as measured provider usage.
Exceptions finalize an interrupted manifest when possible; the raw journal remains the
partial record. No automatic retry or post-hoc replacement. Complete-run replay checks
the entire study order, prompt/selection/state transitions, scores and final selections.

Save the exact protocol, training inputs, source snapshot, configuration, backend identity
and file hashes. Run into an exclusive directory. No validation/test streams are loaded.
Acceptance requires all 240 attempt slots accounted and exact offline replay, not positive
utility. Report fallback and training outcomes without significance or novelty claims.

This single fixed training suite does not provide independent benchmark blocks for the
utility-study statistical plan. Before live or confirmatory use, add block data plumbing,
freeze model/budgets and failure handling, calibrate inference, and preserve holdout access.
