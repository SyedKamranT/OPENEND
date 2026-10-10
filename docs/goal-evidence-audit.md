# Full-goal evidence audit — 2026-10-10

The goal remains active. Prior work is **progress**: source changes, completed local experiments, and verified negative/diagnostic evidence changed the next action. It is not completion of the full discovery architecture.

| Required capability/evidence | Current authoritative evidence | Status and next proof needed |
|---|---|---|
| Identify underrepresented regions | `src/openend/search.py`: distances to three reference signatures | Partial proxy only. Needs a frozen, representative knowledge/solution corpus and calibrated density/coverage diagnostics. |
| Direct generation toward those regions | `openend.agents` constructs reachable probe-cell witnesses; `openend.coordinator` supplies targets and measures attainment | Engineering implementation present. Witness density is not knowledge density; benefit and generality remain unestablished. |
| Preserve quality-diverse candidates | Bounded expression policies, executable training evaluator, 6×6 archive, logged selection traces | Implemented for one narrow software domain. Generalized domains and recombination remain incomplete. |
| Autonomous multi-agent coordination | `openend.coordinator`: serial generator, critic, recombiner, deterministic retrieval and verifier, budget accounting and journal; six-call critic calibration with exact behavior checks | Prototype present, but Qwen 4B critic failed the fixed correctness gate even with full scoring instructions. Tool-grounded claim enforcement, broader role evaluation and full crash-resume remain missing. Older scaffold packages are not the active implementation. |
| Frozen retrieved knowledge corpus | `openend.corpus` and a content-hashed four-note primary-source seed, alongside the broader literature map | Seed foundation only. Needs broader lawful source evidence, independently evaluated retrieval coverage, algorithm details and leakage controls. |
| Adversarial prior-art search and reliable novelty labels | Exact syntax/probe screen; complete-domain index-free equivalence checker; local lexical retrieval | Incomplete. Certificates cover three references only; corpus recall, semantic retrieval, adversarial coordination and independently labeled decisions remain missing. |
| Executable utility validation | Independent packing certificates, reference implementations, frozen splits, replay | Implemented narrow pilot. Strong external algorithm-search comparators, more tasks, fresh holdouts and objective safety/resource limits are still needed for broad claims. |
| Difficult for ordinary prompting/retrieval systems to reproduce | Coordinator v1 includes independent-generation and retrieval-conditioned controls with shared call/token ceilings | Not established. One engineering seed cannot establish superiority; faithful strong search comparators and adequately sized comparisons remain needed. |
| Distinct high-value corpus-novel discoveries | v2 Qwen/Gemma: 192 valid candidates; Qwen v3: 96 valid, one seed worse under sparse targeting; no utility-screen successes | Not demonstrated. Positive novelty/utility cannot be asserted or guaranteed; preserve negative evidence and test better-founded mechanisms. |
| Independent expert evaluation | `docs/hypotheses.md` H5 and ethics planning only | Not conducted. Requires an explicit study protocol, independent reviewers, consent and appropriate recruitment authorization. Do not send recruitment messages automatically. |
| Reproducible scientific contribution | Saved configs/source/events, matching v2 replay, literature correction, descriptive reports | Partial. Confirmatory design/power, independent units, stronger baselines, broader prior art and full-scope evaluation remain open. |

## Current implementation sequence

1. Completed bounded step: versioned probes, legacy replay, and Qwen v3 comparison; no quality gain was established.
2. Completed bounded step: conservative three-reference equivalence certificates and a frozen four-note lexical retrieval seed. Broad prior-art coverage and retrieval/verifier accuracy remain unmeasured.
3. Coordinator v1 now wires serial local generator/critic/recombination/verifier roles, conventional-generation/retrieval controls, shared budgets, no-improvement fallback and novelty abstention. See `coordinator-v1-protocol.md` and the run manifest before duplicating a trial.
4. Next: evaluate retrieval and role quality, expand provenance-backed evidence, and add faithful strong search baselines. Preregister matched component ablations before further model runs.
5. Expand tasks and independent novelty assessment; design fresh confirmation and expert assessment. Audit full requirements before any goal-complete claim.

This sequence preserves the full goal. A successful bounded pilot or a passing test suite does not satisfy the missing rows above. Sparse proxy gains, expression uniqueness, and a model's own judgments are not evidence of novel invention.
