# Shared-grammar baseline adapters: engineering protocol v1

Frozen before model requests, 2026-10-13. Output `results/raw/baseline-adapters-qwen4b-v1`.
This is engineering validation, not a faithful native Python reproduction or efficacy trial.

Three conditions: fixed-reference independent generation, EoH-inspired JSON adaptation,
and FunSearch-inspired JSON adaptation. Each gets 24 calls, 60,000 accounted tokens,
512 output tokens per request and local installed Qwen 3.5 4B with existing backend
decoding settings. One seed (42); seeded condition order. No retries. Every failure,
duplicate and malformed response consumes an attempt and its usage. Fatal transport,
identity or usage failures stop the whole study. Conservative byte-based admission is
the existing backend convention, not a certified tokenizer bound. No cloud or downloads.

All use the existing float evaluator and 48 training streams. No validation/test data
are loaded. Training-only fallback is the best reference if no strict bin-count gain;
report training-best generated policy separately. Report the 1% utility screen but
do not interpret a positive training result as confirmation.

EoH adaptation: population size four; eight initial proposals; then four proposals per
operator e1/e2/m1/m2, in order. Parent selection and objective-deduplicated survivor
selection follow the pinned v0.1 mechanics. Offspring do not change the population
within a batch. Keep a short mechanism description alongside each expression. If the
initial population is empty, stop that arm rather than silently injecting a good seed.
JSON expression/description prompts replace original Python/thought prompts. Original
parser/duplicate retries are disabled, rather than awarded free calls. These are explicit
deviations; this experiment cannot be labeled a native EoH reproduction.

FunSearch adaptation: four islands initially seeded with training-best reference;
per-stream negative bin scores plus negative total bins inserted last; cluster by
sorted score vectors. Use source-derived cluster temperature and length preference;
sample clusters with replacement, and order examples worst to best. Python RNG replaces
NumPy RNG, JSON expression lengths replace Python-source lengths, and expression-version
examples replace native function-completion prompts. Reset the weaker half every 12
attempts (including failures), with source-style small Gaussian tie noise and survivor
founders. This attempt clock replaces the upstream wall clock. These are adaptations.

Acceptance: all 72 attempted requests accounted, no unresolved journal entries, zero-call
replay matches requests, scores, parent selection, population/cluster transitions, resets
and selected outputs. Validity/utility are reported rather than acceptance thresholds.
Incomplete or truncated candidates remain visible. Do not extend this trial to obtain
positive performance. Source fixtures and deterministic state tests precede inference.

Even successful engineering completion leaves native baseline fidelity, independent
novelty labels, retrieval evaluation, power justification and fresh confirmation open.
