# Probe representation pilot v3

Recorded before v3 model generation, 2026-10-10. Phase 1 remains open.

This exploratory representation refinement retains the v2 evaluator, local model, output grammar, prompt, sampling settings, seeds, archive resolution, candidate allowances, token limits, and utility threshold. It replaces the shared behavioral panel in both arms: the 32 original synthetic cases plus 64 hash-pinned training-trajectory cases. The training rows include 32 exact fits and 64 mixed-feasibility decisions, balanced by family and exact-fit stratum. Forced placements are excluded because scoring policies cannot change them.

The descriptor remains mean normalized residual capacity and mean relative bin position. Position is now `index / max(1, bin_count - 1)` for each probe; this is identical to the historical `index / 5` on six-bin probes. Feasible-choice checks reject invalid probe states. The sparsity formula remains mean distance to the nearest two of the same three fixed references plus the existing 0.05 sampling floor.

Run `configs/local_probes_v3.json` with Qwen 3.5 9B, `--backend local --structured`. Three paired seeds, 16 attempts per arm, 96 attempts total. Do not change settings or extend the run based on observed results. New artifacts go in `results/raw/local-qwen35-9b-probes-v3`. Preserve the v2 runs. The Qwen run is a bounded first evaluation of the changed representation; cross-family v3 replication remains subsequent work.

Every run saves the complete panel, training provenance, and content hash in `probe_panel.json`. Archive construction, selection, sparsity, audit signatures, reports, and replay use the same saved representation. Legacy configurations omit the new field and retain the legacy panel. Replaying older runs must remain exact before v3 generation starts.

Primary descriptive comparison remains sparse-on versus sparse-off within this panel. Report validity, actual parent/probe divergence, final selected test bins/fitness, utility-screen success, and resource usage. Coverage cells and probe distances have changed meaning across representations, so v2/v3 coverage is not directly comparable as an improvement metric. No significance, equivalence, or corpus novelty claims follow from this development study. The existing holdout has already been inspected and cannot serve as a new confirmatory holdout.

The broader goal still requires directed generation toward target regions, a frozen retrieved knowledge corpus, adversarial prior-art verification, recombination/critique coordination, conventional-generation/retrieval baselines, stronger utility benchmarks, and independent expert assessment. Probe refinement alone does not complete that goal.

## Completed result and next action

The [v3 report](qwen-probes-v3-results.md) records 96/96 valid policies, 53,450 tokens, 917.1 seconds of request wall time, and 21/48 differing paired parent behaviors. All 15 artifact checks passed and replay matched every score, probability vector, parent selection, and archive update. Qwen was unloaded after completion.

The selected generated policies tied at 1,484 test bins in seeds 42 and 137. In seed 2024, sparse-off selected 1,484 bins and sparse-on selected 1,525. Mean on-minus-off difference was +13.67 bins (worse), and coverage difference was -0.01852 within this representation. Utility-screen successes were zero. This is descriptive negative evidence, not a powered rejection of all sparse-targeting architectures. Selection here is among generated candidates; the initialized archive still contains the known references, so this is not evidence that an operational fallback must use a worse policy.

Do not launch more probe-only trials to seek a positive seed. Next implement and validate conventional-generation/retrieval baselines and budgeted generator/critic/recombiner/verifier coordination, with explicit target-region conditioning and conservative no-improvement/novelty-abstention outputs. Review the three-reference density proxy separately. Corpus and equivalence components added during the run were not injected into its generator or used to change this protocol.
