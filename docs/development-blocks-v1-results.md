# Development blocks and failure accounting — 2026-10-14

Completed the [fixed offline protocol](development-blocks-v1-protocol.md): eight
independently seeded development blocks, two paired search seeds per block, twenty attempts
per arm. All 640 attempt slots completed. Each block contains separately seeded training
and development-evaluation suites, each with twelve streams per family and sixty items
per stream. These public datasets are development data, not a confirmatory holdout.

`development_blocks.py` derives stream seeds from version/master seed/block/role/family/
index. Tests check reproducibility, role separation, stable stream prefixes when suite
size grows, and agreement of expression references with independent imperative packers.
No change was made to the historical suite generator or its seeds. Pseudorandom seed
separation supports the sampling design; it does not prove statistical independence.

`block_runner.py` finishes every search before scoring any development-evaluation suite.
It saves all selected policies and a hash commitment before evaluation, records that hash
in the manifest, and verifies the file remains unchanged afterward. This is auditable
local sequencing, not externally authenticated holdout custody. It checkpoints completed
blocks and preserves partial journals on failure. No live model command is provided.

## Observed result

All 640 proposals were valid, and all 32 arm-runs selected their training-best reference
fallback. All eight block-mean paired differences were zero on development evaluation. The overall
selected-policy mean difference was zero across sixteen paired runs. This is descriptive
negative evidence under the tested offline mutation/budget/grammar conditions. It does
not establish equivalence, adequate power, or impossibility for an LLM-backed search.
The summary returns `insufficient_variation_or_blocks` and a null interval rather than
zero-width certainty. Extra seeds on an identical fallback output would not solve that
precision problem.

Preserve `results/raw/development-blocks-offline-v1`, including per-block datasets and
journals, runs, selection commitment, evaluation, protocol, source and manifest.

```powershell
.venv\Scripts\python.exe -m openend.block_runner replay results/raw/development-blocks-offline-v1
```

## Missing-outcome bounds implemented

Validation: 640 attempts replayed exactly, 29 artifact hashes verified, 119 tests passed.

`failure_bounds.py` supplies an additional diagnostic for incomplete future studies.
For a specified suite, any feasible complete packing uses between the sum of its
instance lower bounds and the total number of items. An observed arm gives a point;
an unknown arm retains that full range. Subtract arm ranges within each planned pair,
average within blocks, and weight blocks equally. The exact planned pair roster is
required: omitted or duplicated pairs are errors, as are observed counts outside bounds.

For example, two planned differences of 1 and an unknown value between -4 and 4 give
finite-study mean bounds [-1.5, 2.5]. Completing the missing outcome narrows the bounds.
Tests verify this for every integer completion and reject removal of the missing pair.

These are **identification bounds for the planned finite-study mean**, not confidence
intervals for a population effect. They assume the missing quantity denotes a feasible
complete output, do not establish that a failed run produced such an output, and cannot
repair unequal realized budgets, unknown token usage or outcome-dependent interruption.
Use them as an explicitly scoped sensitivity analysis, never as a replacement for failure
records or a claim that an incomplete study is complete.

## Effect on Phase 1 closure

The block-data and selection-before-evaluation mechanisms now work in a replayable
offline experiment. Failure-aware descriptive bounds are implemented. The remaining
scientific decisions are still substantive: final interval method under zero-heavy
outcomes; justified practical margin/sample size; faithful strong-baseline comparison;
broader source evidence and deferred independent labels; and independently controlled
confirmation. The next development experiment should localize proposal/search limits,
not enlarge the budget until a positive result appears.
