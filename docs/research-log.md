# Research log and continuation handoff

Updated: 2026-10-10. **Phase 1 remains reopened and provisional.**

## Current direction: local inference

**Refinement completed (2026-10-10):** Read [refinement-findings.md](refinement-findings.md) and [refined-pilot-protocol.md](refined-pilot-protocol.md) before the earlier smoke-test notes below. The training-only schema calibration passed 6/6 after one preserved converter-compatibility failure. Refined Qwen and Gemma each completed 96/96 valid policies. Different parents occurred in 29/48 and 10/48 paired positions respectively; neither showed selected-test quality improvement or any utility-screen success. Both passed all 13 artifact checks and full score/selection/archive replay. The implementation has **40 passing tests** and passes Ruff. Both models were unloaded. Do not overwrite the runs or restart Azure.

**Next continuation:** The original probes contain no exact fits. A concrete counterexample and a tested training-derived replacement candidate are saved in the findings and `data/benchmark/training-probes-v3-candidate.json`. The candidate has 64 reachable, balanced training states with 32 exact-fit cases and is **not active in search**. Before another model run, integrate variable-bin-count positional normalization and a versioned panel behind an explicit configuration, test the feature/feasibility boundary cases, and record a new protocol. Keep the current v2 runs unchanged. Assess the three-reference sparsity corpus as a separate limitation; do not tune seeds or success thresholds to obtain a positive result. A fresh holdout is needed for any confirmatory claim.

The user replaced the cloud plan with local LLM inference on 2026-10-10. Do not retry Azure as the next step. Hardware and model assessment, settings, and rationale are in [local-model-plan.md](local-model-plan.md). Ollama and Qwen 9B/4B, Gemma 12B, and DeepSeek 8B were already installed; no download was needed. The local backend is connected to loopback only and does not read `.env`.

The first connected local study uses `configs/local_pilot.json`, Qwen 3.5 9B Q4_K_M, and `results/raw/local-qwen35-9b-v1`. It records actual model responses, usage, timings, seeded sampling, model digest, and the same objective evaluator as the offline control. The local adapter tests brought the suite to 37 passing tests. See its final report/status before continuing; never overwrite this directory.

**Completed local result:** [Qwen 9B report](local-qwen35-9b-results.md). All 24 attempts completed with accounted usage: 14 valid, six invalid, four truncated; 11,430 total tokens; 491.2 seconds of request wall time. All three pairs had zero outcome differences and zero utility successes. Critically, **0 of 12 paired parent selections differed**, and paired response texts were identical. This is a successful connectivity/evaluator calibration, but an uninformative test of the treatment's benefit: it did not realize different parent choices. It does not establish equivalence or disprove sparse targeting.

All 13 artifact-hash checks passed, and replay matched the 14 valid candidate evaluations without inference. Qwen was unloaded after the run; no model was left resident. Next, improve grammar compliance using training-only calibration and predeclare a longer pilot with parent-choice divergence diagnostics. Do not select seeds because they produce a desired result. Repeat the resulting protocol with Gemma after calibration; do not add a critic at the same time. Old raw artifacts and the run's source snapshot remain unchanged.

## Authorized objective

Correct the research foundation, implement one credible benchmark and shared evaluator, and compare sparse targeting on/off with the model, budgets, archive, and evaluation held constant. The user authorized implementation and API retesting after updating `.env`.

## Completed

- Corrected the literature map and bibliography, narrowed the research question, and revised hypotheses, protocol, ethics, publication plan, and proposal manuscript. The historical review remains in `docs/research-review-2026-10-08.md`.
- Implemented `src/openend`: deterministic online bin-packing inputs, bounded JSON policy interpreter, independent packing-certificate checker, independently implemented first/best/worst-fit references, shared QD archive, and paired sparse-on/off search. Only parent-selection weights differ between arms.
- Added separate offline mutation and configured-model API backends, explicit budgets and failure accounting, exclusive run directories, artifact hashes, source snapshots, verification, replay, and Markdown reporting. `.env` credentials are excluded from snapshots and logs.
- Locked the environment in `uv.lock` and exported hashed `requirements.lock`. Legacy YAML configs now point to the active JSON pilot configurations.
- Final checks: **31 tests passed**, Ruff passed, **13 artifact hashes verified**, and replay matched **400 saved candidates** with zero API calls.

## Observed result

See [the generated results report](pilot-results.md). The complete local run is `results/raw/offline-pilot-final` (ignored by Git; preserve separately when moving workspaces).

Five paired seeds, 40 attempts per arm, 400 attempts total. Every selected policy used 1,484 bins across the held-out test suite. Both arms had zero candidates passing the predefined utility-success screen. Mean sparse-on minus sparse-off coverage was -0.0055556, approximately -0.56 percentage points; selected test bins and fitness differences were zero.

This is an **offline mutation pilot**, not evidence about hosted-model performance, statistical equivalence, or novel discovery. Novelty beyond exact reference matches remains unresolved; Novel-Success Rate is unavailable. No confirmatory significance claim is supported.

## Live API blocker

The latest configured Azure retest, `results/raw/api-pilot-v4`, still returned HTTP 401. A separate API-key-only check of the configured resource's models endpoint also returned 401 with the provider's invalid-subscription-key-or-wrong-endpoint message. No successful model-generated comparison exists. Failed attempts are retained; unknown usage is not treated as zero-cost successful experimentation.

Earlier local attempts are `api-pilot-attempt1` (sandbox connection failure), and `api-pilot-v1`, `api-pilot-v2`, `api-pilot-v3`, `api-pilot-v4` (authentication failures). The adapter now disables further actual requests after a terminal failure within a study. Do not keep retrying without a configuration change. Never paste credentials into chat or print `.env`.

## Continue here

1. Read this log, `docs/pilot-results.md`, `docs/experimental-protocol.md`, and `docs/benchmark-bin-packing.md`. Preserve existing user changes and raw runs; do not restart the review from scratch.
2. Continue with local Ollama inference using `configs/local_pilot.json` and the local-model plan. First inspect the completed Qwen run and its invalid/truncated outputs. Calibrate generation using training feedback only; then repeat selected comparisons with Gemma as a separate within-model experiment. Keep one model loaded at a time. Do not revive Azure unless explicitly requested.
3. Verify and replay any completed run, generate a separate report, and distinguish live-model evidence from the offline control. Incomplete runs cannot support a treatment-effect conclusion.
4. Before locking Phase 1 or running a confirmatory study, finish broader prior-art coverage, independent novelty adjudication, stronger comparators, sample-size justification, and a fresh confirmatory holdout. Do not tune to the already inspected test split and then present it as untouched confirmation.

```powershell
.venv\Scripts\openend.exe verify results/raw/offline-pilot-final
.venv\Scripts\openend.exe replay results/raw/offline-pilot-final
.venv\Scripts\openend.exe report results/raw/offline-pilot-final --output docs/pilot-results.md
# Local inference; choose an unused path:
.venv\Scripts\openend.exe run --config configs/local_pilot.json --backend local --model qwen3.5:9b --output results/raw/my-next-local-pilot
```

The manuscript was revised as a proposal; a LaTeX build has not been verified. The final offline run contains the source snapshot used at execution time; subsequent reporting-format fixes do not alter its saved evaluations. No deployment or publication was performed.
