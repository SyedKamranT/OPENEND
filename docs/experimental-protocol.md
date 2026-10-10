# OPENEND executable pilot protocol

**Status: PROVISIONAL / pilot v1.** No confirmatory preregistration or scientific sign-off is implied.

## Shared comparison

Both arms use the same candidate grammar, generator backend/model, system prompt, mutation operator, training/test suites, initial references, 6?6 archive, replacement rule, seeds, output cap, token allowance, and final scoring. Only elite-parent sampling differs: uniform versus fixed-reference sparsity weights. The model is never told an arm label. Parent prompts can differ because the selected parent differs.

Offline and API experiments are distinct studies: seeded tree mutation is an engineering control, not a substitute for an LLM result. API settings come from `.env` at run start; empty temperature means omitted. Provider-returned model names are logged; differing models within an arm or between its paired arms invalidate the complete comparison. API stochasticity is not removed by local random seeds.

## Executable allowances

| Configuration | Seeds | Generated attempts per arm/seed | Total reported-token ceiling per arm | Maximum output per request |
|---|---|---:|---:|---:|
| `configs/pilot.json` | 42, 137, 2024, 4096, 8192 | 40 | 150,000 | 2,048 |
| `configs/api_pilot.json` | 42, 137, 2024 | 4 | 20,000 | 2,048 |

`.env` may lower the per-request output cap symmetrically. Three common reference evaluations initialize each arm and are logged separately from newly generated attempts. Every attempted generation is retained, including invalid JSON, truncated output, API failures, and duplicate policies. No automatic SDK retries and no unlogged repairs. A terminal API error disables later network requests for that study; skipped requests are explicitly marked.

A conservative UTF-8-byte estimate plus 512 overhead tokens and the output cap reserves allowance before each API call. This is not a provider-certified input token bound. Actual input/output/total usage is reconciled after each call, including reported reasoning-token details. Unknown usage or an overrun makes the comparison incomplete; the runner stops that arm rather than silently dropping the event. Raw request counts and usage are reported, not fictitious FLOP parity. API cost/energy is not inferred without provider pricing/measurement.

## Data access and selection

Training, validation, and test each contain 12 streams per distribution (48 streams, 60 items each). Splits have distinct fixed generation seeds. The generator sees only the task contract, a selected parent, and its scalar training fitness. All arms and seeds finish generation before validation/test scoring. The selected output is the generated valid candidate with greatest training fitness, ties broken by earliest attempt. Validation/test scores never select or modify candidates in this pilot. All valid candidates are also audited, not just the winner.

These are development holdouts. They are not future confirmatory holdouts once used for engineering decisions. The evaluator can be extended only under a new version, with previous data retained.

## Representation and archive

A fixed panel of 32 feasible decision states produces a vector of chosen bin indices. Hamming distance is the fraction of differing decisions. Sparsity is mean distance to the nearest two of three frozen reference signatures. The reference population does not update during a run. The QD descriptors are mean chosen normalized residual gap and mean chosen normalized bin position on this panel. Both axes use six bins over [0,1], with the upper endpoint clipped to the final bin. A cell replaces its elite only for strictly higher training fitness. These are behavioral proxies, not semantic or mechanism-equivalence proofs.

## Execution boundary

Only validated JSON expression trees are interpreted. There is no `eval`, `exec`, generated import, file/network primitive, user function, loop, or recursion construct in the candidate language. Nodes, depth, constants, response bytes, and benchmark sizes are bounded. Division and numeric saturation have deterministic definitions. A separate certificate checker validates assignments and capacity after packing. The interpreter runs trusted project code; this is not an OS sandbox and must never be advertised as one. Arbitrary Python generation is out of scope until an independently tested containment system exists.

## Novelty audit

The same final screen handles all arms. Exact reference-policy hashes imply known-reference status. Other policies are unresolved, even if every probe differs. Syntax identities and finite probe fingerprints are reported separately. No positive novelty labels are generated. NSR stays `null`; its lower/upper bounds describe unresolved labeling uncertainty only. A future independent literature/equivalence audit is required for H4.

## Artifacts and replay

Each output directory is created exclusively; existing runs cannot be overwritten. `run_manifest.json` records UTC timestamps, resolved config, backend settings (never keys), prompt identity, model/usage status, platform, Git commit/dirty state, hashes of actual source including untracked files, and input/output hashes. `source.zip` snapshots an explicit source allowlist and excludes `.env`. Dataset and corpus manifests are materialized per run. `events.jsonl` is flushed after every search attempt; `runs.json` adds final audit results; `analysis.json` contains paired descriptive comparisons.

`openend verify RUN` checks recorded hashes. `openend replay RUN` recomputes candidate evaluation and paired summaries without any model call. Raw model text, prompts, and usage metadata are retained. The reference screen is reproducible; fresh hosted-model requests are not guaranteed identical. Files are tamper-evident against their manifest, not protected by an external immutable storage service. Failed/interrupted runs retain their manifest and partial events.

Runtime/API/dev dependencies are resolver-locked in `uv.lock`; `requirements.lock` is its hashed export. Run `uv sync --locked --all-extras --cache-dir .cache/uv`. Core evaluation itself uses only Python's standard library. The supported interpreter range is in `pyproject.toml`; only the tested platform/interpreter should be described as verified.

## Interpretation and outstanding lock decisions

Reports show raw paired outcomes and exclude incomplete pairs from aggregate comparisons while retaining them visibly. There are no pilot p-values. Model availability, a broader frozen novelty corpus, independently adjudicated labels, strong external algorithm-design baselines, task-level power/precision, confirmatory effect margins, and a fresh controlled holdout are still needed before a scientific lock.

## Local inference amendment (2026-10-10)

Phase 1 remains open. The active model-backed calibration uses local Ollama rather than Azure. `configs/local_pilot.json` specifies three paired seeds, four attempts per arm, a 20,000-token per-arm ceiling, and a 512-token output cap. The shared benchmark/evaluator and sparse-parent-selection treatment remain unchanged. See [local-model-plan.md](local-model-plan.md) for hardware, fixed sampling parameters, 8K context, model lineage, transport restrictions, and the distinction between equal allowances and measured consumption. Existing offline/cloud artifacts retain their original configurations. This is development calibration on previously inspected inputs, not a fresh confirmatory experiment.
