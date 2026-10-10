# OPENEND

OPENEND studies whether sparse-region targeting helps discover useful, distinct solutions beyond matched quality-diversity search.

**Current status: Phase 1 reopened; literature review corrected and in progress; executable bin-packing pilot available.** This repository does not yet demonstrate validated novel discoveries or a statistically established advantage. See [research specification](docs/research-question.md), [benchmark contract](docs/benchmark-bin-packing.md), and [research log](docs/research-log.md).

## Run the pilot

Python 3.11?3.13 is supported by the package; validation so far targets Python 3.11 on Windows. Core evaluation uses the standard library. With uv installed:

```powershell
uv sync --locked --all-extras --cache-dir .cache/uv
.venv\Scripts\python.exe -m pytest -q --basetemp .cache/test-tmp
.venv\Scripts\openend.exe run --config configs/pilot.json --backend offline --output results/raw/my-offline-run
.venv\Scripts\openend.exe verify results/raw/my-offline-run
.venv\Scripts\openend.exe replay results/raw/my-offline-run
```

Use a new output directory for each run. Existing artifacts are never overwritten. On POSIX systems, executables are under `.venv/bin/`.

The offline backend is a deterministic tree-mutation control. **Current research uses local Ollama inference**, as authorized on 2026-10-10. Start with an already installed model:

```powershell
.venv\Scripts\openend.exe run --config configs/local_refined_pilot.json --backend local --structured --model qwen3.5:9b --output results/raw/my-refined-local-run
```

See the [hardware assessment and local experiment plan](docs/local-model-plan.md). This uses a loopback-only endpoint, an 8K context, and no cloud credentials. Each paired comparison holds the model and inference settings constant. Run one model at a time.

The [first connected Qwen 9B pilot](docs/local-qwen35-9b-results.md) completed 24 attempts with 14 valid policies. No paired parent choices differed, so its equal outcomes do not establish treatment equivalence. See the research log for the calibration steps still needed.

The [refined protocol](docs/refined-pilot-protocol.md) adds schema-constrained generation, longer fixed runs, and selection diagnostics. Read [refinement findings](docs/refinement-findings.md) for completed results and remaining limitations, including the original probe panel's lack of exact-fit cases. Reproduce scores and parent-selection traces with `openend replay RUN`.

The legacy cloud backend remains available for reproducibility, but is not part of the current plan:

```powershell
.venv\Scripts\openend.exe doctor --env .env
.venv\Scripts\openend.exe run --config configs/api_pilot.json --backend api --output results/raw/my-api-run
```

The API pilot permits at most 24 requests (three seeds ? two arms ? four attempts), each capped at 2,048 output tokens or a lower `.env` limit. A shared per-arm token allowance is also enforced, with unknown usage/overruns marked incomplete. It uses the model/deployment already specified in `.env`; no model is silently substituted. API failures are retained and terminal errors disable further requests within that run.

Copy `.env.example` to `.env` only when creating a new configuration; preserve any existing credentials. `doctor` prints presence booleans, never keys. API calls use the Responses API with no server-side storage requested. For Azure API-key authentication, configure a matching resource endpoint and key. HTTP 401 indicates authentication is unresolved; an incomplete comparison is not a research result.

## What the implementation measures

Both arms share one 6?6 QD archive design, generation/mutation operator, budget, reference set, probe panel, evaluator, and train/validation/test inputs. The only treatment is uniform versus reference-relative sparse parent sampling. The generator cannot access held-out instances or feedback.

The benchmark includes four synthetic stream distributions and independent first-fit, best-fit, and worst-fit references. Candidate expressions are bounded JSON data, never executable Python. A separate certificate checker verifies complete feasible packings. See [protocol](docs/experimental-protocol.md) for the exact grammar, fitness, stopping, and accounting rules.

Reported outcomes include held-out bin counts, coverage, duplicates, syntax/probe diversity, utility-success screens, and measured API usage. All non-reference novelty judgments remain unresolved. Novel-Success Rate is `null` until independent prior-art assessment exists; probe distance does not establish invention.

## Artifacts and layout

- `src/openend/`: actual package, evaluator, policy interpreter, QD search, API adapter, runner, CLI.
- `configs/pilot.json`, `configs/api_pilot.json`: shared validated configurations. Older YAML files are superseded pointers, not executable full-system configurations.
- `data/benchmark/binpack-pilot-v1/`: reproducible development inputs and reference scores.
- `results/raw/`: ignored local runs, including failed runs; each has manifests, events, results, and a source snapshot.
- `docs/`: current protocol, reviewed literature, limitations, and historical review.
- `paper/`: proposal manuscript and corrected bibliography; no unsupported result claims.
- `uv.lock`: resolver-generated runtime/API/dev dependency lock; `requirements.lock`: hashed export.

Source snapshots explicitly exclude credentials. Output-file hashes are tamper-evidence against a local manifest, not externally immutable storage. Replaying saved candidates is distinct from obtaining identical fresh responses from a hosted model.

## Research milestones

[phases.md](phases.md) supplies the canonical numbering. Phase 1 remains open while novelty adjudication, a broader corpus, strong comparator implementations, sample-size justification, and a fresh confirmatory holdout are unresolved. Phase 2 is a source-verified map in progress. The Phase 3 pilot evaluator is implemented to make calibration possible. Broader agents, independent novelty verification, expert studies, and confirmatory experiments remain future work.

Negative and inconclusive outcomes are preserved and publishable when methodologically sound. [Review and repair rationale](docs/research-review-2026-10-08.md).

The [completed offline pilot report](docs/pilot-results.md) records 400 attempts across five paired seeds with no selected-test performance improvement from sparse targeting. See the [research log and continuation handoff](docs/research-log.md) for verification results, the unresolved Azure authentication failure, and next steps.
