# Fixed-parent opportunity assay v1

Prospective training diagnostic, 2026-10-25, before execution. Four fixed parents:
First Fit, Best Fit, Worst Fit, historical 1475-bin witness. Use existing 48 training
streams and legacy probes. Per parent attempt 128 mutations using common seeds
2026102500..2026102627, unchanged mutation and finite proposal parser. All 512 attempts
count, including invalids and duplicates. Cache evaluations; no adaptive extension.

Endpoint per attempt: max(0, 1476-child_bins); invalids zero. Also count strict parent
improvements, 1%/5% screen passes, distinct policies and parent probe agreement.
Compare exact empirical expected gains under uniform four-parent mixture and normalized
(.05 + reference distance) weights. This fixed pool is not a dynamic archive experiment.
The witness is a diagnostic control, not a novel discovery. Report negative outcomes.

Reused training only; no model calls, native Python execution, new holdout or statistical
inference. Mutation results do not establish LLM proposal behavior. Freeze source and
protocol, retain every response/score. Success thresholds stay unchanged.
