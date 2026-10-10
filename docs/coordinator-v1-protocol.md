# Coordinator v1 engineering protocol

Recorded before local model calls, 2026-10-10. The full goal and Phase 1 remain open.

## Purpose and bounded run

Validate actual coordination, accounting, source provenance, target feedback, and replay before a larger scientific comparison. Use installed **Qwen 3.5 4B**, selected explicitly for this engineering trial to reduce turnaround time. This is a new model setting, not a continuation of the Qwen 9B v3 efficacy pilot. All four conditions use the same 4B model digest, 8K context, temperature 0.7, 512-output-token cap, benchmark, schema and evaluator.

`configs/coordinator_smoke_v1.json`: seed 42; six calls and 40,000 reported tokens allowed per condition; 24 total role calls maximum. Condition order is shuffled once from seed+909. The two coordinated conditions spend two of their six calls on critique, leaving four policy-producing calls; each baseline has six policy-producing calls. This overhead is part of the end-to-end comparison, not free reasoning. Actual token use and time are recorded and need not be identical. There is no efficacy/power claim from this single-seed integration trial.

## Conditions and agent roles

- **Independent:** each call starts from the best training reference, with no generated-candidate feedback or retrieved notes in the prompt.
- **Retrieval:** the same independent baseline, augmented by a fixed query against the frozen four-note source corpus. No adaptive feedback or critique.
- **Coordinator uniform:** repeated generator → critic → recombiner cycles. The generator receives an archive parent; the critic receives the proposal, training score, conservative reference-equivalence result and source leads; its bounded query retrieves further leads for recombination. The recombiner receives a second archive policy and the critique. Valid generated policies are evaluated and retained by the shared QD archive.
- **Coordinator targeted:** identical cycles and uniform archive-parent sampling, with explicit underrepresented-region targets supplied to generation and critique. A separate RNG chooses targets so merely enabling target selection does not consume the parent/model RNG streams. Archive evolution can subsequently diverge.

These are separate logical local-model roles executed serially on one model, not independent models or expert judgments. Retrieval and reference-equivalence checking are deterministic tool roles. The controller validates outputs, accounts usage, selects parents, updates the archive, and gates reporting. It never promotes a model's novelty assertion into a verified claim.

## Reachable targets and evidence limits

Build a probe-only witness library using one bounded mutation of each standard reference, 64 draws per reference, seed 12001; no model calls or fitness/holdout queries are used. Deduplicate behaviors within descriptor cells. Target-cell weights are inverse to witness-behavior count plus prior target visits plus current archive occupancy. Thus targets are rare reachable witness regions, not arbitrary empty cells that may be impossible. Record witness policies, selection probabilities, desired examples, and measured target attainment. The witness policy itself is withheld from role prompts. The 96-case v3 probe panel is frozen and saved with the run.

This witness distribution is **not** a representative human-knowledge corpus. Retrieval uses the existing frozen four original review notes, with unmeasured recall. Certificates establish some equivalences only to first/best/worst-fit under the bounded integer contract. All other novelty remains unresolved. Neither a target hit nor no retrieval hit counts as invention.

## Budgets, failures, and outcomes

Every role call has a pre-call journal entry, schema, prompt, sampling seed, reservation and post-call usage record. Byte-based admission is conservative, not a guaranteed tokenizer count. Unknown usage, model changes, transport failures and token overruns stop the study; unstarted conditions are not imputed as zero-quality completed runs. Invalid policies/critiques consume calls without repair. An invalid proposal falls back to its recorded parent for critique; invalid critique yields no advice for recombination. Interrupted calls remain unresolved in the journal and are never automatically retried. Full crash-resume is not yet implemented.

All conditions finish generation before held-out scoring. A generated candidate must pass the training utility screen (1% aggregate improvement and no family over 5% worse than the best aggregate reference) to replace the reference fallback. Eligible candidates are selected by training fitness only; otherwise the controller explicitly reports no training improvement and retains the known reference. Best-generated test scores are also reported, so fallback cannot hide weak generation. The test screen is an audit, not a candidate-selection signal. No validated novel-discovery count is invented.

Replay regenerates role requests, retrieval, target selection, candidate scores, certificates, archive evolution and fallback decisions using saved responses, and checks the request/response journal. Source, corpus, probes and datasets are hashed. This is local tamper evidence, not an externally immutable preregistration. Strong baselines, independent retrieval/verifier evaluation, larger task-level comparisons, fault-resume and expert assessment remain required for the full goal.

```powershell
.venv\Scripts\python.exe -m openend.coordinator run --config configs/coordinator_smoke_v1.json --output results/raw/coordinator-qwen35-4b-v1
.venv\Scripts\python.exe -m openend.coordinator replay results/raw/coordinator-qwen35-4b-v1
.venv\Scripts\python.exe -m openend.coordinator report results/raw/coordinator-qwen35-4b-v1 --output docs/coordinator-v1-results.md
```
