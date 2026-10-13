# Deeper representation diagnostic v2

Frozen before scoring on 2026-10-13. This is development evidence, not confirmation.
Output: `results/raw/representation-deep-v2`. No model calls or holdout access.

Generate at most 4,096 proposals with Python Random seed 20261013. Use the existing
13 schema leaves and eight operators, depth at most four and at most 31 nodes.
Even-numbered proposals are random trees; odd-numbered proposals add a random
depth-three expression to negative gap. Random subtree expansion stops with probability
0.30 or at depth zero. At the root require an operator. Operators/leaves are uniform.
Duplicates consume proposals and retain their scores; there is no fitness selection.

Score the fixed 48 training streams. Stop at the first policy with strictly fewer
total bins than the training-best reference and no family using over 105% of that
reference's bins, or after 4,096 proposals. Report the existing 1% utility screen
separately. A one-bin training gain is an expressibility witness, not utility success.
Save all attempted policies/scores, the exact generated plan, source, this protocol,
training data, and full packing assignments for the selected best policy.

Replay must verify every saved score, plan prefix, stopping decision and assignment
certificate. No-improvement means only that this fixed sampled search failed; this is
neither exhaustive nor a proof about the complete grammar. Do not extend the budget
or change the seed after seeing the result. New searches require a new protocol/version.
