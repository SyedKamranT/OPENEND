# Refined local pilot v2: prospective development protocol

Recorded 2026-10-10 before calibration and generation. Phase 1 remains open.

## Diagnosis and decisions

The first local run completed but produced 14/24 valid policies; JSON mode admitted wrong arity and strings masquerading as expressions. All 12 paired parent choices matched. At the initial archive, sparse probabilities differ only slightly from uniform: first/worst-fit weight 0.39375 versus best-fit 0.45625. This is a weak contrast, not evidence of a broken sampler or evidence of equivalence. The fixed-reference sparsity definition and weights remain unchanged to avoid tuning the treatment to obtain a favorable result.

First calibrate only output grammar on training data: six requests, standard reference parents in first/best/worst order repeated twice, seeds 9001 through 9006, fixed Qwen 3.5 9B. Accept if at least five are valid and none has transport/usage/model-identity failure. No candidate is chosen by validation or test performance. Preserve rejected calibrations rather than silently repairing outputs.

The new shared JSON schema restricts features and constants, operator arity, and nesting. Four operator levels permit at most 31 nodes. Constants are {-2, -1, -0.5, 0, 0.5, 1, 2}. This is a narrower proposal space than the earlier grammar, applied equally to both arms. The independent evaluator retains its original grammar and checks. Add explicit JSON syntax examples, keep temperature 0.7, 8K context, 512 output tokens, thinking off, and six CPU threads. Schema decoding follows [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs); validation still determines whether an output is accepted.

## Fixed continuation after acceptance

Use `configs/local_refined_pilot.json`: seeds 42, 137, 2024; 16 attempts per arm per seed (96 per model); 40,000 tokens allowed per arm; 512 output tokens per attempt. Run Qwen 9B, unload it, then repeat the same configuration and schema with Gemma 12B as a separate within-model replication. Do not add a critic, change the sampler, choose seeds based on divergence, extend a run until significant, or alter success thresholds.

Record every pre-selection probability vector, archive policy IDs, and total-variation distance from uniform. Report paired parent-choice divergence, validity/truncation, syntax/probe diversity, archive coverage, held-out selected fitness and bins, utility-screen success, usage, and latency. All generation within a study ends before holdout scoring. Compare sparse on/off within a model; do not claim that equal tokens across tokenizers imply equal compute. Model name, digest, schema, prompt, sampling options, and source are recorded per run.

If calibration fails, preserve it and revise the grammar using training diagnostics before writing a new prospective amendment. Transport failure invalidates the affected comparison rather than triggering retries. Invalid candidates consume attempts normally. If the longer run still has no changed parents or no improvement, report that finding; it does not justify searching for favorable seeds.

These are descriptive development experiments on an already inspected benchmark, not confirmatory tests or independently adjudicated novel inventions. A new confirmatory holdout, stronger external comparators, and novelty review remain required. Equality or a single positive seed will not establish effectiveness.

### Compatibility amendment before any successful calibration response

The first schema request was rejected by the installed converter: it requires `items` to be an object and rejects the standard boolean `items: false`. Preserve `local-grammar-calibration-v2` as a failed transport/schema-compatibility attempt (one sent request, five suppressed calls). Remove that redundant keyword; exact tuple lengths remain enforced by `minItems` and `maxItems`. Repeat the unchanged six-request calibration in `local-grammar-calibration-v2b`. A separate diagnostic request reproduced HTTP 400 without generation.

### Calibration gate outcome

`local-grammar-calibration-v2b` passed 6/6, all with known usage and valid policies. Generated outputs were 10–20 tokens. This authorizes the fixed continuation above; it does not prove general validity or higher policy quality. Training scores were recorded, but no holdout was scored and no candidate was selected to initialize the study. All studies still start with the same three references.

### Completed fixed continuation

Both 96-attempt studies finished without changing the protocol. See [refinement-findings.md](refinement-findings.md), [Qwen results](refined-qwen35-9b-results.md), and [Gemma results](refined-gemma3-12b-results.md). A subsequently prepared candidate probe artifact is diagnostic only and was not used by either experiment.
