# Phase 4 adapted-baseline protocol v2 — preparation draft

Status: preparation only; no new model experiment launched. This describes the
existing shared-JSON track and its required completion work, not native reproduction.

All arms must use the same frozen online host, total training-bin objective, finite
proposal grammar and training streams. Score every invalid/duplicate returned attempt
against its arm's call budget; retain started calls, returned calls, known tokens,
unknown usage and stopped runs. Equal allowance does not imply equal realized tokens.
Report both. Current archived v1 settings (24 calls, 60000 tokens, population/islands 4,
reset interval 12, seed 42) remain engineering settings, not a powered study design.

| Choice | Shared-JSON adaptation |
|---|---|
| Independent generation | Fixed best-reference parent with training score |
| EoH initialization | Two population-sized generated batches; no initial reference population |
| EoH operators | e1/e2/m1/m2 in population-sized batches; no within-batch offspring feedback |
| EoH M3 | Present upstream, excluded from pinned default four-operator sequence; disclose |
| FunSearch initialization | Best reference registered in each island |
| FunSearch representation | Whole JSON expressions rather than Python completion |
| Score disclosure | Numerical parent scores exposed; differs from native FunSearch prompt |
| FunSearch reset | Attempt-based, including invalid attempts; differs from wall-clock resets |
| Proposal enforcement | Shared server-side four-level finite grammar, independent of backend |
| Selection | Freeze training-only selected policy before any development evaluation |

Before executing the next comparative run, freeze the model digest, block/seed list,
per-arm allowances, evaluation assignment and failure aggregation in a new config.
Require a useful online signal justification or label the run solely engineering.
Audit score-temperature behavior and differing initial information explicitly. A
native reproduction requires the pinned Python prompt/evaluator contract and contained
candidate execution; do not relabel these adapters as native EoH or FunSearch.

The narrow OPENEND claim needs a matched uniform-versus-fixed-reference-weight contrast.
These three adapted baselines alone do not test that intervention. Stronger mechanism
claims additionally need the Phase 2 comparator obligations. Phase 4 remains open.
