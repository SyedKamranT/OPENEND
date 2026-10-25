# Baseline fidelity audit v2 — 2026-10-15

> Follow-up: [evaluator audit v3](baseline-fidelity-v3.md) now documents executable action-space and objective witnesses. The remaining differences below are historical as of v2.

Status: additional source-based state tests pass. The implementations remain **shared-JSON
adaptations**, not faithful native EoH or FunSearch reproductions. No new inference ran.
Upstream versions and all thirteen pinned source/license files remain unchanged.

## What was checked

`tests/unit/test_baseline_state_fidelity.py` extracts individual reviewed methods from
hash-verified upstream files. It imports no upstream client and executes no model-generated
program. Upstream model/evaluation calls are replaced by fixed proposal fixtures. This
test harness is not a general Python sandbox or a full native execution test.

For EoH, the test executes pinned `InterfaceEC.population_generation`, `EOH.run`,
`EOH.add2pop` and the population manager. It checks two initialization batches and two
full generations of e1/e2/m1/m2 at population size four: forty supplied proposals with
ties and failures. Every local batch sees the same population as upstream; final survivors
match. Operator weights are fixed at one; a controlled always-active branch replaces
NumPy's random draw. This verifies batch timing, not stochastic operator-weight fidelity,
parallel evaluator behavior, timeout handling, parsing, retries or native code quality.

For FunSearch, tests execute pinned `Island.register_program`, `Cluster.__init__`,
`Cluster.register_program` and `ProgramsDatabase._register_program_in_island`. They check
duplicate registrations, distinct signatures sharing a total score, grouping, registration
counts, strict best replacement and first-best retention on ties. Existing differential
tests separately check the actual upstream signature and scalar-reduction functions.

## Fidelity matrix

| Mechanism | Evidence | Remaining difference or gap |
|---|---|---|
| EoH rank selection | Differential seeded draws against pinned function | Python seed orchestration remains explicitly adapted |
| EoH objective-deduplicated survival | Differential function tests and main-loop fixture | Native evaluator objective/scaling must be audited |
| EoH initialization/batch schedule | Pinned initialization/main-loop execution matches local population state | Population four versus pinned default five; bounded 24-call trial versus default generations |
| EoH operator ideas | Local i1/e1/e2/m1/m2 tasks correspond to source intent | Prompts are paraphrases, JSON replaces Python, thought format changes |
| EoH score feedback | Local parents include training bin counts | Pinned operator prompt examples contain descriptions/code, without these numerical scores: additional information is an adaptation |
| EoH parsing/retries | Local attempts fully accounted | Upstream malformed/duplicate retry behavior is not reproduced; upstream rounding and evaluation still need audit |
| FunSearch signature/reduction | Differential pure-function tests | Negative aggregate bins appended last is a benchmark mapping |
| FunSearch registration/best retention | Pinned method execution matches fixtures | Python dictionary/program representation replaces native functions |
| FunSearch probability calculations | Local unit checks only | NumPy dtype/SciPy softmax correction and distribution equivalence not differentially validated |
| FunSearch sampling | With-replacement cluster sampling, score-ordered examples implemented | Python RNG/JSON lengths; equal-score ordering may differ from NumPy argsort |
| FunSearch islands/reset | Local reset/founder fixtures | Four islands versus pinned default ten; twelve attempts versus four-hour wall clock; serial execution |
| FunSearch prompts | Scored JSON version examples | Native function headers, docstrings, recursive renaming and completion parsing not reproduced |
| Native evaluator/containment | Not established | No verified generated-Python containment; do not equate subprocess timeout with isolation |

The defaults above are read from the pinned `getParas.py` and `implementation/config.py`,
not inferred from current upstream main. All source paths, commits and hashes are recorded
in `data/baselines/upstream-v1/manifest.json`. Relevant upstream paths:

- EoH: `eoh/src/eoh/methods/eoh/{eoh.py,eoh_interface_EC.py,eoh_evolution.py}`.
- FunSearch: `implementation/{programs_database.py,config.py}`.

Do not use the number of passing tests as a percentage of reproduction fidelity. The
untested prompt/evaluator/representation differences may materially affect performance.

## Local backend compatibility finding

During integration inspection, the new utility runner called `generate(**request)` with
a `schema` keyword. The existing `LocalBackend.generate` parameter is `output_format`.
Offline/scripted backends accepted `schema`, masking a future live-call TypeError. The
runner now passes the four arguments positionally; replay receivers use the same contract.

The runner also recognizes the backend's actual `incomplete_response` status as a charged,
nonaccepted attempt. Previously it would classify that status as unexpected and stop.
A dedicated test deliberately uses the local parameter name, returns twelve incomplete
responses, verifies all usage is charged and no policy accepted, and replays the result.
The CLI still exposes no live utility execution, so this issue caused no failed live
utility experiment. Historical completed offline output is unchanged and replay-tested.

## Before another model-backed baseline comparison

Use a new protocol and output directory. Preserve the interrupted 54-start/53-response
trial and unknown last usage. Specify whether the next question compares adapted search
mechanisms or reproduces native methods; it cannot answer both under an unlabeled JSON port.
Pin objective/evaluator and all representation/prompt/init/reset deviations. Charge every
retry, invalid proposal and model-role call. Verify model identity, output cap and context
at the integration boundary, and define interruption/replacement rules prospectively.

The next source-audit priority is the upstream bin-packing evaluator and native prompt
construction, followed by actual NumPy/SciPy probability comparisons in a reproducible
test environment. No independent-review labels or Phase 1 closure are inferred here.
