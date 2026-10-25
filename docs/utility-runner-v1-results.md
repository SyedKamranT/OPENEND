# Total-bin utility runner: engineering result

2026-10-14. The [prospective offline protocol](utility-runner-v1-protocol.md) completed
240 attempted mutations: three paired seeds, forty attempts per arm. All 240 policies
passed the finite grammar and were evaluated on existing training data. No LLM calls,
provider tokens, validation/test access or fresh holdout generation occurred.

The new runner uses total bins consistently for archive replacement, model-facing parent
feedback and final selection. It keeps historical fitness-based runners unchanged.
It records started/processed requests, scores, probabilities, full archive state, valid
candidate ordinals, failures, fallback and source/input/output hashes. The command-line
interface permits offline execution and replay only; live backend behavior is tested with
scripted responses, not claimed as provider-verified.

## Outcome and intervention check

| Seed | Final cells, uniform / weighted | Best generated bins, uniform / weighted | Paired attempts with different parents | Weighted mean total variation from uniform |
|---|---|---|---:|---:|
| 42 | 6 / 6 | 1,476 / 1,476 | 16 / 40 | 0.162907 |
| 137 | 5 / 5 | 1,476 / 1,476 | 7 / 40 | 0.185652 |
| 2024 | 8 / 8 | 1,476 / 1,476 | 12 / 40 | 0.143278 |

All six runs selected the Best Fit fallback at 1,476 training bins, because no generated
policy strictly improved it. Uniform selection has total variation zero by construction.
The weighted probabilities were materially different, and parents differed in 35 of
120 paired attempt positions. These position-wise comparisons include downstream archive
differences; they are not a controlled estimate of an individual selection's causal effect.

This demonstrates that the intervention was active while utility remained unchanged in
this finite trial. It is neither a superiority result nor proof of equivalence, model
failure, or impossibility. Equal final cell counts do not imply identical cell contents.
Three search seeds on one reused training suite are not independent benchmark blocks.
No confidence interval or H4 discovery-yield estimate is appropriate here.

## Validation and artifacts

Saved-response replay matched all 240 prompts, seeded selections, scores, archive states
and final selections with zero new inference. Tests cover finite grammar violations,
duplicate response fields, unknown usage, identity changes, invalid attempts, admission
before dispatch, nontraining-data rejection and preservation of an unresolved request
when a backend throws an exception. The tests do not prove arbitrary provider behavior.

Preserve the ignored directory `results/raw/utility-offline-v1` when moving workspaces.
The exact protocol and source snapshot used are included. Reproduce verification with:

```powershell
.venv\Scripts\python.exe -m openend.utility_runner replay results/raw/utility-offline-v1
```

## Next gate

The total-bin state is now integrated into a budgeted training-only runner. Remaining
work includes independently generated development blocks, objective-matched comparators,
explicit treatment of failed pairs, robust inference for zero-heavy outcomes and a
prospective model-backed protocol. Do not scale calls merely to seek a positive result.
First identify whether proposal quality or the search intervention limits improvement,
using controls fixed before execution. Native baseline fidelity and external review
remain separate unfinished requirements; neither prevents this engineering work.
