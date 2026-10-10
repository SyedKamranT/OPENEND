# Coordinator engineering pilot

Status: **completed**. Model: `qwen3.5:4b`.

All conditions share call/token ceilings. Critique consumes those allowances; candidate counts differ intentionally. This is an end-to-end feasibility comparison, not a powered efficacy test.

| Seed | Condition | Calls | Valid policies | Valid critiques | Target hits / attempts | Best generated test bins | Fallback | Selected test bins | Outcome |
|---:|---|---:|---:|---:|---:|---:|---|---:|---|
| 42 | independent | 6 | 6 | 0 | 0/0 | 1484 | True | 1484 | no_training_improvement |
| 42 | coordinator_uniform | 6 | 4 | 2 | 0/0 | 1495 | True | 1484 | no_training_improvement |
| 42 | coordinator_targeted | 6 | 4 | 2 | 0/4 | 1484 | True | 1484 | no_training_improvement |
| 42 | retrieval | 6 | 6 | 0 | 0/0 | 1484 | True | 1484 | no_training_improvement |

| Seed | Condition | Accounted tokens | Request seconds | Utility successes |
|---:|---|---:|---:|---:|
| 42 | independent | 3710 | 36.4 | 0 |
| 42 | coordinator_uniform | 5355 | 95.8 | 0 |
| 42 | coordinator_targeted | 6437 | 109.7 | 0 |
| 42 | retrieval | 5468 | 26.7 | 0 |

The target witness library uses generated probe behaviors, not a comprehensive knowledge corpus. Source retrieval uses four reviewed notes with unmeasured recall. Known-reference equivalence can reject some rediscoveries; all other novelty remains unresolved. These roles share a local model and are not independent expert judgments.

All generation precedes holdout scoring. Fallback selection uses training data only; best-generated scores are the test results of each condition's training-best generated candidate, reported separately so fallback cannot hide poor generation. The reused pilot holdout is exploratory, not fresh confirmation. No global novelty or statistical superiority is asserted.
