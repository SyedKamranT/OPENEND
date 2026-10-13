# Pinned baseline fidelity foundations

2026-10-13. **Primitives and source fixtures, not completed EoH/FunSearch baselines.**
No baseline model experiment has been run and no performance comparison is supported.

Saved 13 public implementation/license files in `data/baselines/upstream-v1`, retaining
original bytes as `.txt`. `manifest.json` records repository, commit, ref, original path,
download URL and SHA-256. Tests verify every file and both licenses.

| Baseline | Selected source | Immutable commit |
|---|---|---|
| EoH | Official legacy v0.1 release | `4b2338fc2317c743cec50c5c7a2e4684707af973` |
| FunSearch | Official main resolved on 2026-10-13 | `cc53f274237d7ab05c19df939edbc1f9616a7c19` |

EoH's current README distinguishes its new API from legacy v0.1. The pinned release is
the explicit reproduction target here; it is not assumed to exactly reproduce every
published paper setting. [Official version guidance](https://github.com/FeiLiu36/EoH).

## Mechanisms now implemented and checked

`openend.baseline_mechanics` supplies the following building blocks:

- EoH draws parents with replacement using weights `1/(rank+1+population_size)`.
  Differential tests compare 20 draws across each of 25 identical RNG seeds to the
  pinned upstream function.
- EoH removes failed objectives, retains the first candidate for each distinct objective,
  and selects the lowest objective values. Equal-score syntactically distinct programs
  can disappear, leaving fewer survivors than the nominal population size. Fixtures
  cover ties, failures, and five population-size requests.

These match the pinned [rank selector](https://github.com/FeiLiu36/EoH/blob/4b2338fc2317c743cec50c5c7a2e4684707af973/eoh/src/eoh/methods/selection/prob_rank.py)
and [population manager](https://github.com/FeiLiu36/EoH/blob/4b2338fc2317c743cec50c5c7a2e4684707af973/eoh/src/eoh/methods/management/pop_greedy.py).

FunSearch signatures sort test keys, while scalar reduction takes the **last inserted**
score. Differential fixtures distinguish these orders. A benchmark adapter explicitly
appends negative total bins last; otherwise a naive per-stream mapping would optimize
the last stream. This objective mapping is an adaptation and must be reported. The
temperature schedule and length-weighted probability helpers have deterministic tests;
they do not yet have NumPy/SciPy upstream differential coverage.
[Pinned database implementation](https://github.com/google-deepmind/funsearch/blob/cc53f274237d7ab05c19df939edbc1f9616a7c19/implementation/programs_database.py).

The test harness extracts only four inspected functions from verified source bytes;
it does not import upstream model clients or execute generated candidate programs.
This narrow AST extraction is not a general-purpose security sandbox.

## Fidelity risks identified before building runners

The EoH snapshot implements `m3`, but its default operator list is `e1,e2,m1,m2`.
Its prompt layer also retries malformed output, which must consume any matched model
budget. The main loop updates population state between operator batches. Freeze the
exact operator schedule and initialization in the reproduction protocol; do not
silently infer defaults from a paper summary or switch to current main.
[Pinned defaults](https://github.com/FeiLiu36/EoH/blob/4b2338fc2317c743cec50c5c7a2e4684707af973/eoh/src/eoh/utils/getParas.py),
[prompt/parser implementation](https://github.com/FeiLiu36/EoH/blob/4b2338fc2317c743cec50c5c7a2e4684707af973/eoh/src/eoh/methods/eoh/eoh_evolution.py).

FunSearch still requires island registration/reset, stochastic cluster and program
sampling, versioned code prompts, and evaluator integration. Its scalar objective and
reset clock need explicit mappings to the shared benchmark. Equal token/call limits
must include every attempted generation, not only accepted programs.

## Next implementation acceptance gate

Build budgeted runners only after prompt, scheduling and state-transition fixtures
match the pinned sources. Keep native Python reproductions separate from shared-JSON
grammar adaptations. Establish isolated execution/time limits for generated Python,
shared training-only scoring, complete journal/accounting and saved-response replay.
Then freeze a small engineering comparison; full efficacy and confirmation remain later.

Final suite at this continuation: **90 tests passed; Ruff passed**. This test count
covers the whole repository, not 90 baseline fidelity cases. There are six new baseline
test functions and six new deeper/numerical-diagnostic tests.
