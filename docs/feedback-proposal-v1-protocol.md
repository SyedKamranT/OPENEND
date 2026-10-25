# Matched proposal feedback pilot v1

Frozen before requests on 2026-10-25. Adaptive training-only pilot; 12 calls, no powered
inference, no fresh evaluation, no native Python. Keep the current four-level finite
proposal grammar and original 48 training streams. No outcome-based budget extension.

Parents: Best Fit and the historical 1475-bin witness, fixed throughout. Seeds:
2026102601 and 2026102602 for each parent. Three conditions: none, beneficial, mixed.
For each parent/seed pair shuffle condition order with Random(seed + parent_index).
No offspring or other-condition outcomes are fed to later requests.

Model: installed local qwen3.5:4b, digest
`d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04`.
Use existing LocalBackend settings: temperature .7, top_p .95, top_k 20, repeat_penalty
1, presence_penalty 0, six threads, think false; 8192 context, 256 output tokens.
Each condition gets four calls and a 40000 total-token ceiling. Report realized tokens;
allowances are equal, prompt lengths are not. Mixed adds examples, so this is the effect
of adding harmful evidence, not an isolated valence effect at equal input length.

Examples are interventions by `neg(abs(sub(gap,mul(1,item))))` on saved BF states.
From the hashed phase4-decision-v1 input, sort by instance_id and step; take the first
two beneficial states from distinct streams and first two harmful states from distinct
streams. Verify each label by replaying the saved prefix and action followed by BF.
Beneficial receives the same two positives as mixed; mixed additionally gets two
negatives. None gets no examples. All receive the same intervention expression and
warning that labels use BF prefixes/completion and cannot label new-policy states.
No future items or stream IDs appear in model examples. No-example is not information-free:
it still receives the parent, total score, objective and common task instructions.

Require at most one non-root subtree replacement with at most seven replacement nodes;
allow exact copies but charge them. No root replacement, repair or retry. Invalid,
out-of-bound and incomplete responses consume calls; full performance scoring is only
for eligible completed responses. Count every status. Fallback at policy selection is
the supplied parent: accept only strictly fewer bins and no family worse than 105% of
that parent's family total. This fallback is selection-time, not a new runtime operator.
Report raw candidates even if rejected. Do not confuse improvement over BF with beating
the supplied global 1475 incumbent or passing the unchanged 1461 / reference-family screen.

Primary: selected total bins per matched parent/seed, including fallback; secondary:
raw total, per-family totals, copies, empirical agreement with reference training
trajectories, BF-state diagnostics, four-panel reference distance and own complete
packing certificates. Empirical reference agreement is not universal equivalence.
No archive weighting is used; reference distance does not measure underexploration.

Freeze all requests, config, inputs, protocol and source before first call. Append and
flush a started record before transport and response record immediately on return.
Stop the entire run on transport failure, model change, missing/invalid usage or budget
overrun; preserve unknown usage and unresolved starts. No automatic restart/resume.
Replay saved responses and recompute scores/certificates without model calls. The parent
and current-state inputs remain online even though their development uses training hindsight.

After this pilot, freeze any chosen procedure before new development data. Regardless
of outcome do not access final confirmation. A negative result does not justify extending
this seed list. Published nonlinear controls and native baselines remain pending separately.
