# Deeper representation audit and numerical sensitivity

2026-10-13. Training-only diagnostic under the [prospective protocol](representation-v2-protocol.md).
No model calls, validation/test queries or confirmatory holdout access.

The fixed search stopped at proposal **2,566 / 4,096**, the first eligible training
improvement. It evaluated 2,429 distinct policies; duplicates consumed attempts.
The selected policy used **1,475 bins**, versus **1,476** for best-fit, a reduction
of one bin (approximately 0.068%). It did **not** pass the existing 1% utility screen.

```text
add(neg(gap), max(mul(item, sub(remaining, gap)), gap))
```

Here features are normalized. In exact arithmetic `remaining - gap = item`, so the
score simplifies to `max(item² - gap, 0)`. This selects the tightest feasible bin
when its gap is below the squared normalized item size; otherwise all scores tie
and the host chooses the earliest feasible bin. This algebraic explanation is not
a novelty judgment. Prior-art distinctness remains unresolved.

| Family | Best-fit | Selected policy |
|---|---:|---:|
| Uniform | 403 | 403 |
| Bimodal | 406 | 405 |
| Paired | 404 | 404 |
| Triplets | 263 | 263 |

Under the production float interpreter, individual differences are: `train/bimodal/001`
35→34, `train/paired/001` 35→34, and `train/paired/006` 33→34. Other stream bin counts
are unchanged. There is a tradeoff even in this tiny aggregate gain.

## Numerical audit performed after discovery

The cancellation in the discovered expression motivated a separate diagnostic.
`openend.numerical_audit` evaluates the same bounded operators using exact rational
features/constants, retains protected division and clipping, and checks packing
certificates. This is a sensitivity analysis, not a change to the frozen evaluator.

| Expression | Production floats | Exact rationals |
|---|---:|---:|
| Discovered expression | 1,475 | 1,475 |
| Algebraically simplified expression | 1,476 | 1,475 |

The original float/exact trajectories diverge on one training stream, although total
bin counts agree. The exact gain survives, but the float result is sensitive to an
equivalent rewrite. Do not equate algebraic equivalence with identical interpreter
behavior, or call this a robust algorithmic improvement. Preserve expression structure
in replay and report numerical semantics in future baseline comparisons.

## Evidence and limits

- `results/raw/representation-deep-v2`: exact plan, protocol, train suite, source snapshot,
  2,566 events, summary and 48 complete packing certificates. Seven artifact hashes
  checked; all attempts, early stopping and certificates replayed exactly.
- `results/raw/numerical-audit-v1`: original-expression float/exact comparison, divergence
  states and exact certificates, plus source snapshot and hashes.
- `results/raw/witness-simplification-v1`: separately preserved post-hoc rewrite audit.

Both numerical audits also recomputed exactly. After the run, summary selection was
hardened to retain an eligible stopping witness even if an earlier lower-total candidate
violated family constraints; the saved selection is unchanged. A regression test covers
that case. Final suite: **90 tests passed; Ruff passed**.

This establishes that the present language can express a small gain on the reused
training suite. It does not establish useful improvement, generalization, an advantage
for language-model search, or novel discovery. Stopping at the first weak witness
means the run provides no estimate of the best achievable policy or success frequency.
The original 1,053-policy shallow negative result remains unchanged.

Next: use this as a fixed positive example for representation/reproduction diagnostics;
finish strong baseline adapters and their fidelity checks. Do not evaluate this witness
on a fresh holdout while using it to tune the method.
