# Coordinated scoring sketches v1

Declared 2026-10-25 before evaluating this candidate set. Adaptive training diagnosis,
not confirmation or a matched search-method comparison. Input: the existing 48 training
streams and saved `phase4-decision-v1/report.json` Best Fit traces. No new split access.

Question: can bounded, coordinated score changes express the eight previously observed
beneficial deviations, and do those choices survive complete online execution?

Enumerate eight target expressions in order: constants 0.1, 0.2, 0.3, 0.4, 0.5,
then item multiplied by 0.5, 1, 2. For each target t evaluate:

- residual preference: `-abs(gap-t)`;
- plateau: `max(-gap,-t)`;
- triangular adjustment: `w*min(gap,t-gap)-gap`, w in 0, 0.5, 1, 2, 4, 8.

Exactly 64 charged sketches, no early stop, retries, additional grids or outcome-based
extension. Zero weight is the predeclared Best Fit ablation; every target and weight is
reported, including duplicates. Add five separately labelled controls: First Fit, Best
Fit, Worst Fit, historical 1475-bin witness, and post-hoc max(gap,fraction) bridge from
the previous experiment. The bridge is previously selected training information.

Use the unchanged production interpreter (31 nodes, depth six, bounded constants),
host action rules, tie breaking and numerical semantics. Check every expression against
the narrower current proposal grammar and report eligibility. Finer constants/greater
depth are diagnostic capabilities, not a silent change to the generator. This does not
test cross-bin summaries or exhaust the expression language.

For every candidate report full 48-stream score, certificates, unchanged 1%/5% screen,
gain over 1475, and all four existing reference-distance panels. On all 2880 saved BF
states, look up the chosen action's saved BF-completion bins: count beneficial/harmful/
neutral deviations and coverage of the eight improvable states. These are hindsight
labels used only for diagnosis, not policy inputs or estimates of whole-policy value.
Do not sum state improvements as achievable utility; interventions share prefixes.

Primary diagnostic endpoint: best complete-stream total, alongside generator eligibility
and family screen. Rank best by total then enumeration order, not distance. No selection
advantage or novelty claim. All rules use current item and current bins only.

Save candidate plan before scoring, source, protocol, input hashes, complete certificates
and results. Verify original input hashes and source/protocol stability. Test analytic
limiting cases and check every packing independently. Stop after this finite census.
If useful decisions are expressible but full utility fails, report transfer/regression
failure; do not infer that expanding the grammar will solve it. Any next proposal method
or known published nonlinear control needs a separate frozen specification and reviewed
implementation. No native baseline execution or virtualization changes in this run.
