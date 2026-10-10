# Critic contract calibration v1

Prospective engineering protocol, 2026-10-10, before model requests. Phase 1 remains open.

Use installed Qwen 3.5 4B, the existing native loopback-only backend, 8K context, temperature 0.7, no thinking, 384 output tokens maximum per request. Six calls total; 20,000 total reported token ceiling with conservative admission. No retrieval, retries or holdout access. Save source, requests, cases, training suite, raw replies, usage and journal; stop on unknown usage, transport failure, model change or overrun.

Three fixed policies: `mul(gap,exact_fit)` (first-fit), `neg(remaining)` (best-fit), and `gap` (worst-fit). For each, compare a minimal task prompt against the same prompt plus the generator's complete selection and feature semantics. Use paired seed 16001+case index; alternate condition order. This compares the semantic contract on the **new common structured output format**, not the entire old critic against the new critic. No causal claim about retrieval, prose removal or search utility follows.

Each response must classify the original policy, predict its choices on three fixed feasible-bin states, supply an executable revision and predict that revision's choices on the same states. Ground-truth original labels and vectors are hand-derived in `openend.role_calibration.CASES`; tests check them against the interpreter. Revision predictions are checked by the interpreter and revision utility by the training evaluator. Classification is valid only for these analytically known policies; this is not a general novelty classifier.

Gate: all three full-contract responses must have correct original classes and choice vectors, valid revisions and correct revision choice vectors. Every request must complete with accounted usage. Training utility and behavioral change are separate outcomes, not acceptance requirements. Passing this deliberately small necessary check does not establish robust critique, generality, novelty, or discovery efficacy. Failure means the role remains unqualified for dependable autonomous feedback. Preserve failures; no acceptance-threshold changes after observation.

Run once into `results/raw/critic-contract-qwen35-4b-v1`:

```powershell
.venv\Scripts\python.exe -m openend.role_calibration run results/raw/critic-contract-qwen35-4b-v1
.venv\Scripts\python.exe -m openend verify results/raw/critic-contract-qwen35-4b-v1
.venv\Scripts\python.exe -m openend.role_calibration replay results/raw/critic-contract-qwen35-4b-v1
```

Explicit target controllability and task-specific retrieval calibration remain separate next steps. Do not alter coordinator v1's saved method or infer it improved from this calibration alone.
