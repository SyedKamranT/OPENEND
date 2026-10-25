# OPENEND

OPENEND studies whether fixed-reference behavioral-distance parent weighting improves
training-selected online bin-packing policies over otherwise matched uniform selection.
Utility, behavioral diversity and prior-art novelty are separate outcomes.

**Current status (2026-10-25): Phases 1–3 closed for their documented development scope;
Phase 4 open.** Virtualization/native execution is deferred at the owner's request.
No useful weighting advantage or independently validated novel discovery is established.
See the [research lock](docs/research-lock-v1.md), [Phase 4 acceptance](docs/phase4-acceptance-v1.md)
and [current work order](docs/feedback-action-plan-2026-10-25.md).

## Evidence so far

| Evidence | Supported conclusion |
|---|---|
| 240 offline utility attempts | Weighting changed parents in 35/120 paired positions; all runs selected Best Fit fallback |
| 640 attempts across eight development blocks | All block-mean differences were zero; no equivalence claim |
| Training witness: 1475 versus BF 1476 bins | Small expressible gain; below the 1% screen of 1461; rewrite sensitivity documented |
| 512 fixed-parent mutation attempts | No improvement over the best supplied parent; two responses preserved its known gain |
| Native baseline fidelity audits | State, evaluator, prompt and probability differences measured; native integration unfinished |
| Live baseline v2 | 31 starts, 30 saved responses; interrupted, unresolved usage preserved |

Details: [utility trial](docs/utility-runner-v1-results.md), [blocks](docs/development-blocks-v1-results.md),
[representation](docs/representation-v2-results.md), [proposal diagnostic](docs/parent-opportunity-v1-results.md),
[fidelity](docs/baseline-fidelity-v4.md), [research log](docs/research-log.md).

## Run development checks without virtualization

Python 3.11–3.13 is supported. The original `.venv` pointed to a removed Python 3.11
installation; `.venv-research` is the replacement built from the unchanged dependency lock.
With uv and an installed supported Python:

```powershell
$env:UV_PROJECT_ENVIRONMENT = '.venv-research'
uv sync --locked --all-extras --python 3.13 --cache-dir .cache/uv
.venv-research/Scripts/python.exe -m pytest -q --basetemp .cache/test-current
.venv-research/Scripts/python.exe -m openend.utility_runner replay results/raw/utility-offline-v1
.venv-research/Scripts/python.exe -m openend.parent_opportunity results/raw/parent-opportunity-reproduction
```

Use a new output directory for each experiment. Raw artifacts are local and ignored by
Git; preserve them when moving the project. Optional NumPy/SciPy audit tests require those
packages and otherwise skip explicitly. They are separate from core standard-library evaluation.

The active JSON track interprets bounded expressions as data and does not need Docker.
Native EoH/FunSearch requires verified contained Python execution; see [setup status](docs/native-environment-setup-v1.md).
Do not execute `native_runtime/worker.py` with generated code directly on the host.
Local-only inference remains the plan; the legacy cloud backend is retained for historical
reproduction, not selected by this continuation. Never overwrite existing credentials.

## Design and claim boundaries

Both primary arms share grammar, model/digest, probes, archive, replacement, selection,
stopping and allowances; only parent probabilities differ. Total training bins govern
selection, with earliest generated ties and best-reference fallback. Selection precedes
development evaluation. Public/reused splits are development data, not fresh confirmation.

The 1% aggregate / 5% family utility screen remains fixed. Frozen probe distance is not
semantic equivalence or scientific novelty. Unsupported novelty judgments remain unresolved.
Final inferential calibration and access-controlled fresh data belong to Phase 13.

## Layout

- `src/openend/`, `tests/`: implementation and executable checks.
- `configs/`, `data/`: protocols, source pins and development definitions.
- `results/raw/`: local immutable-per-run evidence, including failures.
- `docs/`: decisions, results, limitations and continuation handoff.
- `paper/`: evolving study manuscript; no superiority claim.
- `native_runtime/`: unverified native execution scaffolding pending containment tests.

[Canonical roadmap](phases.md). Historical results and locks are retained; internal
review acceptance does not imply independent novelty validation.
