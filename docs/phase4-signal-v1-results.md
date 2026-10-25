# Phase 4 signal diagnosis and baseline correction — 2026-10-15

Executed the [prospective protocol](phase4-signal-v1-protocol.md) in full: 84 attempts,
84 distinct policies, no early stopping, no model calls, training data only.

| Diagnostic | Total training bins | 1% / family arithmetic screen |
|---|---:|---|
| Best Fit reference | 1476 | No |
| Best of 84 online candidates | 1476 | No |
| Offline first-fit-decreasing | 1386 | Yes, ineligible as an online policy |
| Offline best-fit-decreasing | 1386 | Yes, ineligible as an online policy |
| Sum of elementary lower bounds | 1352 | Bound only, not a packing |

The offline algorithms save 90 bins (6.10%) and pass all family constraints. Every
assignment is remapped to original item order and independently certificate-checked.
They use future information; their success establishes feasible offline headroom,
not attainability with the online action constraints. Neither is an exact solver.
Their family totals are uniform 386, bimodal 386, paired 360 and triplets 254.

The selected online candidate is max(0.1-gap,0), first among equal minimum-total
candidates. It is production-interpreter valid but outside the current finite proposal
vocabulary. Only 12 of 84 attempted parameterizations fit that vocabulary. None of
those 12, or the expanded set, passes. The historical 1475-bin witness remains better;
this diagnostic does not replace it. No new candidate is promoted to a success claim.

Artifacts: `results/raw/phase4-signal-v1` contains the protocol, source archive, input
suite, all scores, offline and selected online certificates, and hash manifest.

## Concrete baseline defect fixed

The baseline response parser previously validated the general evaluator language but
not the narrower advertised proposal grammar. Nonconforming backends could therefore
admit constants such as 0.05 or five nested operators despite a four-level schema.
The baseline and utility parsers now share a finite-grammar validator. Invalid baseline
responses follow existing invalid-attempt accounting. Six regression cases cover both
defects in all three baseline arms. Old source snapshots/results remain unchanged;
replaying an old run containing these previously admitted responses may now expose a
status mismatch and must use its archived implementation for historical reproduction.

## Research decision

Continue Phase 4 engineering, not a large superiority experiment. The missing signal
is not explained by exhausted offline packing headroom. Online information/action
constraints, representation and search remain competing explanations. Next diagnostic
should measure training decision regret against a bounded hindsight completion oracle,
without feeding future information to candidate policies. Specify its solver limits,
state sampling and stopping rule before execution. Use the resulting counterexamples
to motivate a separately versioned representation experiment; retain fresh evaluation
for later prospective replication. Do not keep sweeping the same data until a win.

Validation: **141 tests passed in 32.53s; Ruff clean.** All 144 saved packing certificates and artifact hashes verified. Saved utility/block replay matched 240 + 640 attempts. No model calls.
