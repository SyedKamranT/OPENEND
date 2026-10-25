# Proposal-operator comparison v1

Frozen before execution, 2026-10-25. Training-only development; no model/native calls.
The baseline operator has already been inspected in parent-opportunity-v1. Therefore
this is an adaptive development comparison, not a blinded confirmatory test.

Four fixed parents: FF, BF, WF, historical 1475-bin witness. Common seeds
2026102500..2026102627. Two operators, 128 charged attempts per parent/operator (1024
records): unchanged subtree replacement, and structurally conservative single-token
mutation. Conservative mutation chooses a node uniformly, changes a terminal to a
different allowed terminal, or an operator to a different operator of the same arity.
It preserves the rest of the tree and does not retry, repair, or resample after validation.
Use actual finite parser, production evaluator, original 48 training streams. Cache
repeated policies globally; duplicates/invalids still count. No early stopping/extensions.

Primary diagnostic: improvement over the best supplied parent (1475), not BF (1476).
Report copies, repeated syntax, exact training-assignment-signature equality to each
parent, per-parent gain, finite-probe equality and distance separately. Training packing
hash equality is empirical agreement, not universal semantic equivalence.

Behavioral reach: use unchanged legacy panel and the three fixed stress panels from
Phase 3. Per panel report how many proposals exceed the maximum fixed-parent reference
distance. Require exceeding all four panel thresholds for the conservative robust-reach
indicator. This is behavioral reach relative to the frozen reference set, not occupancy
of a globally sparse region or proof of novelty. Do not select panels after results.

Retain unchanged 1% aggregate / 5% family screen; report the conjunction of useful
success and robust reach. Select the minimum-total screen passer if any, otherwise the
minimum-total valid proposal, earliest attempted ties. Supplied parents remain incumbents.
If no new useful signal appears, do not promote an operator as better or expand model
spending; specify a new representation diagnostic before further adaptive experiments.
All files, source and protocol hashes saved; no evaluation/holdout access or inference.
