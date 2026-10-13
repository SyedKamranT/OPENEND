# Grounded feedback and controllability calibration v2

Frozen before model calls, 2026-10-13. Development-only engineering gates.
Preserve all earlier runs. New output: `results/raw/grounded-qwen35-4b-v2`.

Nine requests, no retries: three grounded critic cases from critic calibration v1,
then three target-only requests each paired with a witness-exposed control.
The critic gets actual normalized features, feasible-bin scores, choices and tie rules.
It must return an executable revision and predict both original and revised choices.
The host rejects the entire feedback if any prediction is false or any field is invalid.
Accepted feedback contains only computed evidence, revision and measured training-bin delta.
Acceptance does not imply improvement, general reasoning competence or novelty.

Target requests use the same three fixed development states, exact coordinate formulas,
six-bin grid and three distinct reference-reachable cells. Target-only prompts conceal
the witness policy; witness controls expose it. This is an elementary prerequisite:
even 3/3 does not establish controllability on the 96-state search panel. No target
scores or critique revisions update an archive in this calibration. Fixed seeds and
ordering are in `grounded_calibration.requests`; this is not a causal ablation estimate.

Local installed `qwen3.5:4b`, existing LocalBackend decoding settings, 8K context,
384 output tokens/request, 40,000 total-token ceiling, conservative context/token
admission. All calls, errors and usage are saved; missing usage or model identity
changes stop the run. Exactly nine successful accounted responses are required for
completion. Each gate requires 3/3 successes on its own arm; report the gates separately.
There are no adaptive retries or additional seeds after observing results. The v1 versus
v2 comparison is descriptive because the output contract and evidence differ.

The versioned coordinator `coordinator-grounded-v2` enforces the same critic gate
before feedback reaches recombination. v1 behavior and replay remain unchanged.
Do not launch larger efficacy trials just because unit tests pass.

Separate representation diagnostic: enumerate all 1,053 leaves and one-operator
expressions using the schema's 13 leaves, two unary and six binary operators. Score
all against the existing 48-stream training suite, with the existing 1% utility screen.
Save every policy/score, the best single policy and the per-instance hindsight oracle.
The oracle is not a deployable policy. A successful witness proves training improvement
is expressible; zero successes cannot prove the full grammar lacks better policies.
The enumerated set is fixed before its results; no validation or test split is loaded.

Commands:

```powershell
.venv\Scripts\python.exe -m openend.research_diagnostics results/raw/representation-audit-v1
.venv\Scripts\python.exe -m openend.grounded_calibration run results/raw/grounded-qwen35-4b-v2
.venv\Scripts\python.exe -m openend.grounded_calibration replay results/raw/grounded-qwen35-4b-v2
```

Replay checks saved inputs, request order, journal, assessments and summary, with no
model calls. Raw artifacts are locally hash-checked, not an external preregistration.
