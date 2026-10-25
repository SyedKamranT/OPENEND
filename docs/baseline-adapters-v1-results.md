# Baseline adapter trial: interrupted, verified prefix

Date: 2026-10-13. This training-only local Qwen 3.5 4B engineering trial followed
[the prospective protocol](baseline-adapters-v1-protocol.md). It did not meet its
72-request completion criterion. No treatment-effect or native-baseline claim follows.

| Arm | Saved responses | Valid policies | Measured tokens | Best generated training bins | Utility successes |
|---|---:|---:|---:|---:|---:|
| FunSearch JSON adapter | 24/24 | 24 | 14,627 | 1,476 | 0 |
| EoH JSON adapter | 24/24 | 24 | 16,265 | 1,476 | 0 |
| Independent generation | 5/24 | 5 | 2,768 | 1,476 | 0 |

Both complete arms selected the best-fit reference fallback (1,476 training bins).
The incomplete independent arm has five saved responses, followed by a sixth request
with no saved response. That request's reserved bound is 2,966 tokens; actual usage is
unknown. The 53 saved responses report 33,660 tokens. The study must not be reported as
having only 53 attempted calls, or as having complete measured cost. Fifty-four requests
were started; the final request could have consumed resources after its journal entry.

On continuation the execution handle no longer existed, no matching baseline Python
process was found, and Ollama was unreachable. The exact cause of interruption is not
established. The original manifest remains `running`, an archival consequence of abrupt
termination before finalization, not evidence of a live process. No request was retried.

`openend.baseline_recovery` verifies input hashes, reproduces all started requests and
selections, and recomputes all 53 processed responses' scores and state transitions.
It stops at the final unresolved request without synthesizing a provider response.
The reconstructed journal matches the saved journal exactly; the two completed condition
records also match. Recovery used **zero model calls** and left original files unchanged.

Preserve both ignored directories:

- `results/raw/baseline-adapters-qwen4b-v1`: original inputs, source snapshot and journal.
- `results/raw/baseline-adapters-qwen4b-v1-recovery`: verified recovery report and source hashes.

Recompute into an unused directory with:

```powershell
.venv\Scripts\python.exe -m openend.baseline_recovery results/raw/baseline-adapters-qwen4b-v1 results/raw/<unused-recovery-directory>
```

The adapter mechanics have scripted state/replay tests, including an interruption and
corrupted-journal rejection. Their representation, prompts, RNG, reset clock and retry
deviations remain documented. A completed adapter experiment would still not substitute
for faithful native EoH and FunSearch reproductions. Any completion/replacement experiment
needs an explicit protocol amendment retaining these failures and their cost; silently
repeating the unresolved request or extending search until improvement is not allowed.
