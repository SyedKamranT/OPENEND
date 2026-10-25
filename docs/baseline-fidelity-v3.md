# Baseline evaluator fidelity v3 — 2026-10-15

Status: **executable evaluator audit complete for the documented fixtures**. Phase 1 stays
closed. Native method reproduction remains Phase 4 work; current search implementations
remain shared-JSON adaptations. No model inference or performance experiment ran.

## Material findings

Both pinned upstream packing loops allocate one empty bin per item, pass every feasible
bin to the score function, and choose the first maximum. OPENEND scores feasible *opened*
bins and opens another only when none fits. This is a change in the available actions,
not merely a different expression syntax.

| Capacity-100 stream / policy | OPENEND bins | Pinned EoH bins | Pinned FunSearch bins |
|---|---:|---:|---:|
| 40, 40, 20 / Worst Fit | 1 | 3 | 3 |
| 40, 40, 20 / First Fit | 1 | 1 | 1 |
| 40, 40, 20 / Best Fit | 1 | 1 | 1 |
| 60, 40 / Best Fit | 1 | 1 | 1 |

All fifteen packing witnesses are in `results/raw/baseline-evaluator-audit-v1/report.json`.
First/Best Fit agree across all five fixture streams. This is finite fixture evidence,
not a proof of equivalence for arbitrary policies or inputs. Exact fits are eligible in
both upstream implementations despite EoH's prompt wording describing capacities as larger
than the item. The EoH prompt also says full-capacity bins will not be used; the inspected
host loop does not enforce that restriction. A generated scorer may enforce it itself.

EoH's `evaluateGreedy` computes relative excess of mean bin count over a dataset-specific
lower bound, overwriting the result for each dataset and returning the final value.
With injected bound 1, dataset A requiring one bin and dataset B requiring two, order A/B
returns 1.0 and B/A returns 0.0. Its pinned default loader supplies one Weibull dataset:
this witness identifies a multi-dataset extension hazard, not evidence that its default
published evaluation suffers this particular ordering effect. The loader was inspected
as source; its imports, pickle helper and dataset constructor were not executed.

FunSearch's notebook evaluator returns negative mean bins. On the two fixture instances
it returns -1.5 while OPENEND reports total bins 3. For a fixed number of instances these
have the same ranking after reversing sign, but their scales differ. Softmax temperature
makes score scale relevant to search probabilities: ranking agreement alone cannot justify
calling an aggregate-total mapping a native reproduction. No quantitative probability
calibration is claimed by this evaluator audit.

## Prompt construction audit

The existing hash-pinned EoH task requests a NumPy vector score function and explicitly
encourages complexity. Local JSON prompts impose a small expression grammar and provide
parent training-bin counts. Upstream EoH operator examples contain descriptions and code;
the added numerical feedback remains a declared adaptation.

The pinned FunSearch `Island._generate_prompt` orders versioned function implementations,
renames recursive calls, and appends an empty next-version function header with an
improvement docstring. That method does not interpolate parent numerical scores. The local
JSON adapter supplies scored versions and asks for a whole expression. Both the completion
format and score disclosure therefore differ, independently of island mechanics.

## Reproducible audit

Three supplemental files are pinned by commit and SHA-256 in
[the evaluator source manifest](../data/baselines/evaluator-v1/manifest.json).
The original thirteen-file upstream manifest remains unchanged. Licenses are retained in
`data/baselines/upstream-v1`; EoH is MIT and FunSearch is Apache-2.0.

Primary source locations:

- [EoH evaluator at the pinned commit](https://github.com/FeiLiu36/EoH/blob/4b2338fc2317c743cec50c5c7a2e4684707af973/eoh/src/eoh/problems/optimization/bp_online/run.py).
- [EoH dataset loader at the pinned commit](https://github.com/FeiLiu36/EoH/blob/4b2338fc2317c743cec50c5c7a2e4684707af973/eoh/src/eoh/problems/optimization/bp_online/get_instance.py).
- [FunSearch packing notebook at the pinned commit](https://github.com/google-deepmind/funsearch/blob/cc53f274237d7ab05c19df939edbc1f9616a7c19/bin_packing/bin_packing.ipynb).

`src/openend/baseline_evaluator_audit.py` extracts only reviewed evaluator methods from
fixed source hashes. It does not execute whole notebook cells, upstream imports or
candidate-generated Python. NumPy is an audit-environment dependency, not a core runtime
dependency. The executed environment is recorded in the JSON report (NumPy 2.3.4).
Tests skip explicitly if NumPy is unavailable; this continuation ran them in an environment
where it is installed. No dependency installation was needed.

PowerShell reproduction, using Python with NumPy installed:

```powershell
$env:PYTHONPATH = 'src'
python -m openend.baseline_evaluator_audit --output results/raw/baseline-evaluator-audit-reproduction/report.json
python -m pytest tests/unit/test_baseline_evaluator_audit.py -q
```

The output is created exclusively and will not overwrite an existing report. The report
records evaluator pins, manifest hash, implementation hash and environment versions.
Five tests check the action-space counterexample, reference controls, last-dataset
aggregation, negative-mean scaling, and rejection of modified source before execution.

## Decision and next work

Retain the frozen OPENEND evaluator and historical outcomes unchanged. The next adapted
comparison must use that same evaluator and objective in every arm, and be named an
adapted-search comparison. It cannot establish superiority over native EoH/FunSearch.
A native track needs its own prospectively fixed evaluator/action contract, score scaling,
function representation, prompt contract and contained execution before model calls.

Next implement the prospective adapted-baseline protocol with explicit score-feedback,
initialization, reset and failure-accounting choices; numerical sampling fidelity remains
an additional audit item. The public upstream dataset contents inspected here are development
material and cannot be relabeled a fresh holdout.

Validation: full suite **128 passed in 31.83s**; Ruff clean.
