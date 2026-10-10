# Coordinator v1 diagnosis and next gate

2026-10-10. This is an engineering diagnosis, not a positive discovery result. Preserve the v1 source snapshot and responses; do not repair its outputs retrospectively.

## What the connected model exposes

The critic parser checks JSON fields and length bounds, not whether the advice is correct or actionable. In `42/coordinator_uniform/0001`, the weakness is only `The proposed expression [` and the revision is `gap`. In `42/coordinator_targeted/0001`, the revision recommends replacing an expression with the ELM approach and a program-mutation operator. That advice does not specify an executable change within this experiment's expression grammar. Other fields end in incomplete sentences. Count these as schema-valid critiques, not validated reasoning.

The critic system prompt does not include the generator's full feature definitions, score direction, tie-breaking rules or bounded operator semantics. It receives a policy and score but lacks enough task specification to reliably diagnose the policy. Retrieved notes describe search frameworks rather than concrete bin-packing scoring mechanisms. Their relevance to a scoring revision is unvalidated. These are plausible implementation/design causes of poor advice; this pilot does not isolate their causal effects.

The explicit target records give descriptor bounds and two desired examples, but do not fully explain how the descriptor coordinates are computed. A reachable witness proves the cell is attainable within the host interpreter, not that the prompt makes it understandable or that it improves packing utility. Target attainment must be reported independently of validity and utility.

## Next experiment, before expanding the search

Use a separate, versioned **training-only role calibration**, with fixed cases chosen before requests. Do not run more efficacy seeds just to seek a positive result.

1. Give the critic the same complete task/grammar contract as the generator. Ask for a short structured defect category, an executable candidate revision and a concrete feasible-bin example supporting its claimed behavioral change. Prefer bounded structured evidence over length-constrained prose that can terminate mid-sentence.
2. Check the example with the host interpreter and evaluate the proposed revision on training data. Report separately: schema validity, valid executable revision, correct predicted bin choice, behavioral change and training utility. A correct behavior prediction is not proof that the advice improves utility.
3. Include known-reference equivalents and deliberately poor policies. For example, `mul(gap, exact_fit)` is zero for every feasible bin and therefore behaves as first-fit under the defined tie rule. The critic should not describe it as an effective exact-fit preference.
4. Explain target coordinates explicitly and test whether a generator can reproduce a few fixed reachable target behaviors. Separate this controllability check from whether sparse targeting helps search.
5. Compare no retrieval with task-specific retrieved evidence on these fixed cases. Broaden and independently label the retrieval corpus before interpreting a retrieval miss or critic assertion as novelty evidence.

Keep model, decoding, cases and per-condition call/token ceilings fixed within each calibration. Record all failed attempts and actual usage. Predeclare acceptance criteria and a new artifact directory before model calls. Only then run the larger matched search comparison, with fresh confirmation data and stronger algorithm-search baselines. Phase 1 remains open.
