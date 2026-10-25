# Independent development blocks: offline protocol v1

2026-10-14. Fixed before execution. These public inputs are development data, including
the separately generated evaluation streams. No confirmatory holdout is created.

Use eight blocks with master seed 20261014, two paired search seeds (42,137), twenty
attempts per arm and twelve streams per family. Each stream retains the existing family
distribution, capacity 100 and sixty items. Derive its PRNG seed by SHA-256 over generator
version, master seed, block, role, family and stream index. Training and development_eval
roles have different seed domains. Separate streams do not consume shared RNG state.
This is reproducible pseudorandom sampling, not a mathematical proof of independence.

Both arms share training/evaluation data within a block. Run the existing total-bin
offline utility engine: same finite grammar, probe panel, archive and fallback; only
parent weights differ. This is 640 total offline attempts. Do not increase that allowance
after results. No model-backed calls. No critic, retrieval or target-role changes.

Finish all blocks' searches before scoring any development-evaluation streams. Write a
selection file containing every selected policy and its hash before evaluating. Evaluate
only these selected policies on each block's development-evaluation suite. Record the
reference fallback flag and paired total-bin differences. Evaluation cannot select a
different candidate, change a prompt, alter an archive or extend a completed run.

Save per-block started/processed journals, datasets, selected-policy commitment, source,
protocol and hashes. Replay from saved responses with zero generation, including selection
order, state and final scores. Stop on an incomplete block; retain partial artifacts.
Report each block/run and an equal-weight block summary. If all differences are zero,
record insufficient variation rather than a zero-width confidence interval. Even a
nonzero result is descriptive development evidence; no confirmatory p-value or H4 claim.

Acceptance is complete accounting of 640 attempts, training/evaluation separation,
unchanged selections and exact replay. Positive performance is not an acceptance condition.
