# Phase 4 decision diagnosis v1

Prospective protocol, 2026-10-16, before execution. Training-only: the fixed 48 streams.
No model calls, policy search, representation change or evaluation/holdout access.

At every state on a Best Fit trajectory, try each feasible opened bin for the current
item, then complete the original remaining stream with Best Fit. If no bin fits, the
only action is opening a bin. Keep the prefix fixed. Record every action's final bin
count and a full certificate for the best alternative. This is exact enumeration of
one forced action with a fixed continuation, not an optimal-completion solver or a
causal estimate of a learned policy's effect. Do not add savings across overlapping
counterfactuals from the same stream.

Separately run a sequential hindsight rollout. At each actual visited state evaluate
all legal actions with Best Fit continuation; choose the minimum final-bin action,
prefer the normal Best Fit action on ties, then earliest index. Repeat to stream end.
This uses future items and is ineligible as an online candidate, but respects the
frozen no-optional-opening action contract. Check complete certificates and every
choice's host eligibility. Preserve all action values and selected paths.

Fixed budget: all states in both passes, no early stopping, no adaptive data selection.
There are 2*48*60 decision states, at most 60 actions per state and 60 items per
completion (10,368,000 item placements upper bound, excluding feasibility scans).
No recursive or unbounded search. Report family totals, unchanged 1%/5% screen,
count of strictly improvable Best Fit states, and single-deviation best total per
stream separately from sequential hindsight totals. A positive hindsight result
establishes host-constrained headroom, not online learnability or generalization.
