# Research log and continuation handoff

Updated: 2026-10-10. **Phase 1 remains reopened and provisional.**

## Current direction: local inference

**Latest: critic contract calibration completed (2026-10-10), gate failed.** [Results](critic-calibration-v1-results.md) and [prospective protocol](critic-calibration-v1-protocol.md). Added `openend.role_calibration` and four tests. Six local Qwen 4B calls used 2,527 accounted tokens and produced six valid revisions. Both minimal and full-contract prompts scored 0/3 on complete original-choice vectors and 0/3 on revision-choice vectors; full-contract reference classification was 0/3 (minimal 2/3). No training utility successes. The full scoring contract alone did not repair critic reasoning on these cases. This is a small necessary correctness check, not a model-family or search-efficacy conclusion.

All seven artifact hashes and six-response replay passed; **69 tests pass, Ruff passes**. Qwen is unloaded; no live run needs resuming. Preserve `results/raw/critic-contract-qwen35-4b-v1`. Next implement tool-grounded behavioral evidence and enforce claim checks before critic feedback enters search; independently calibrate explicit target controllability. Do not treat valid JSON as correct critique or keep rerunning a failed gate until positive. The full goal remains active.

**Latest continuation: coordinator v1 completed (2026-10-10).** Read [results](coordinator-v1-results.md), [diagnosis and next gate](coordinator-diagnostics.md), and the prospective [protocol](coordinator-v1-protocol.md) first. Implemented serial local generator/critic/recombiner roles, explicit reachable targets, frozen-note retrieval, conservative equivalence checking, shared budgets and independent-generation/retrieval controls. The Qwen 3.5 4B engineering trial completed 24/24 calls: 20 valid policies and four schema-valid critiques, 20,970 accounted tokens, 268.7 request seconds. No utility successes; targeted candidates reached 0/4 target cells. All conditions used the training-selected best-fit fallback (1,484 test bins). The uniform coordinator's training-best generated policy used 1,495 test bins; fallback does not count as a generated improvement.

All **14 artifact hashes verified**, and replay matched all **24 role calls** without inference. **65 tests pass; Ruff passes.** Qwen 4B was unloaded; no experiment is running. Saved raw evidence: `results/raw/coordinator-qwen35-4b-v1` (ignored by Git; preserve separately). The run contains its original source snapshot; the later report-only edit adds actual resource totals and clarifies training-based candidate selection.

**Continue here:** calibrate critic correctness and target controllability on fixed training-only cases before expanding the search. Schema-valid critiques contained incomplete or irrelevant advice; the critic lacks the generator's complete scoring contract, and target prompts lack full coordinate semantics. The four-note retrieval corpus mostly describes search frameworks, not actionable packing heuristics. The [diagnosis](coordinator-diagnostics.md) specifies the next versioned calibration and evidence checks. Do not silently change v1, tune to the reused test split, or rerun until positive. A single engineering seed establishes neither superiority nor impossibility. Phase 1 and the full research goal remain open.

The entries below preserve earlier milestones; their test counts and next-step statements are historical.

**Full-goal continuation (2026-10-10):** The broader discovery-system goal is active; see [goal-evidence-audit.md](goal-evidence-audit.md) for requirement-level evidence and missing work. The 96-case mixed probe panel is now integrated behind `probe_panel: training-mixed-v3` in `configs/local_probes_v3.json`, including variable-bin normalization and saved-panel replay. Both 96-candidate v2 runs replayed exactly after integration. The prospective [v3 protocol](probes-v3-protocol.md) governs `results/raw/local-qwen35-9b-probes-v3`; inspect its manifest before starting any duplicate run.

New verifier/retrieval foundations are documented in [verifier-and-corpus-foundation.md](verifier-and-corpus-foundation.md): complete-domain reference-equivalence certificates identify 11/43 distinct Qwen and 9/22 Gemma v2 policies as known-reference equivalents; a frozen four-note primary-source corpus supports deterministic local retrieval with citations. These components remain outside the v3 generator and do not establish corpus-wide novelty. Current tests: 60 passed, plus the three corpus tests rerun after deterministic ranking cleanup; lint passes. Agent coordination, directed-region generation, evaluated retrieval/verifier coverage, stronger baselines, broader benchmarks and independent review remain unfinished.

**V3 completed:** [Qwen v3 results](qwen-probes-v3-results.md): 96/96 valid, 21/48 different paired parent behaviors, zero utility successes. Selected generated test policies tied in two seeds; sparse-on used 41 extra bins in seed 2024 (mean +13.67 bins). All 15 hashes and full 96-candidate score/selection/archive replay passed. Qwen was unloaded; there is no live experiment to resume. Next work is the missing matched baseline and budgeted agent coordination, incorporating retrieval and conservative verifier components only under a new protocol. Keep Phase 1 and the full thread goal open. Do not reframe the negative pilot as success, rerun until positive, or claim global novelty from the four-note seed corpus.

**Refinement completed (2026-10-10):** Read [refinement-findings.md](refinement-findings.md) and [refined-pilot-protocol.md](refined-pilot-protocol.md) before the earlier smoke-test notes below. The training-only schema calibration passed 6/6 after one preserved converter-compatibility failure. Refined Qwen and Gemma each completed 96/96 valid policies. Different parents occurred in 29/48 and 10/48 paired positions respectively; neither showed selected-test quality improvement or any utility-screen success. Both passed all 13 artifact checks and full score/selection/archive replay. The implementation has **40 passing tests** and passes Ruff. Both models were unloaded. Do not overwrite the runs or restart Azure.

**Historical next step, now implemented as v3:** The original probes contain no exact fits. The 64 training-derived states are now combined with the 32 legacy cases only for explicitly versioned v3 runs; v2 remains unchanged. The three-reference sparsity corpus is still a limitation. Do not tune seeds or success thresholds to obtain a positive result. A fresh holdout is needed for any confirmatory claim.

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
