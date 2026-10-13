# Research upgrade: evidence before larger search

2026-10-13. Phase 1 remains open. This is a staged research plan, not a claim that
all six workstreams are complete. See [new diagnostic results](grounded-calibration-v2-results.md).

Continuation: the [deeper representation audit](representation-v2-results.md) found a
one-bin training witness with numerical sensitivity, while [baseline fidelity work](baseline-fidelity-v1.md)
now pins upstream sources and checks selected mechanics. Full baselines remain unfinished.

## Research claim to earn

At matched resources, does directing generation toward underrepresented *reachable*
behaviors improve independently evaluated utility over strong search baselines?
Treat correct criticism, target controllability, utility, and prior-art distinctness
as different outcomes. A valid policy or an occupied archive cell cannot substitute
for any of them. The current evidence does not establish a benefit.

## 1. Grounded feedback — implemented; model gate failed

`openend.evidence` supplies executable score traces and checked packing trajectories.
Coordinator v2 rejects false choice predictions and unknown prose fields, charges the
call, and sends no rejected feedback to recombination. Accepted feedback is reconstructed
from interpreter outputs and training scores. Rejection and correctness are separate
from whether a revision helps. The three fixed cases are a smoke test only.

Next, define a new, larger training-only case bank with unseen states, no-feasible-bin
cases, ties, protected division, saturation and non-reference policies. Require correct
counterexamples on independently held-back calibration cases. Freeze any prompt change
before testing it. A model need not calculate scores: it can propose a revision while
the host computes consequences. Compare that simpler role with predicted-choice criticism
in a new protocol instead of assuming prediction is useful overhead.

## 2. Controllability — separately measured; gate failed

The new task isolates coordinate targeting from utility and includes witness controls.
The witness-control failure means that even this elementary prompting interface is
unreliable under the tested settings; it does not prove the model can never target.
Before the 96-state panel, establish the ability to copy a supplied executable witness
exactly and to compute its descriptor. Then separate imitation from target-only generation.
For full-panel calibration, balance target cells by reachable witness count, stratify
by distance from the parent, and report cell hit rate, coordinate error and valid-output
rate separately. Compare to untargeted generation on the same fixed requests/budgets.
Witness exposure is a positive control, not a discoverability result.

## 3. Representation — shallow audit completed; deeper question open

All 1,053 one-operator policies were tested on training streams. The best ties best-fit.
The next diagnostic must expand depth under a predeclared enumeration/solver budget,
save per-instance certificates, and stop once a valid training-improving witness is found
or the fixed budget expires. Preserve the failed shallow result. If an improving witness
exists, assess whether the model can reproduce its behavior without revealing its syntax.
If search finds none, report the tested subset and budget, not grammar impossibility.

Audit useful missing information before changing the language: scores currently use an
individual bin, item and normalized index, without general aggregate state or memory.
Add richer features only as a separately versioned representation experiment, then give
all comparators the same information. Keep discovered training witnesses out of confirmation.

## 4. Strong baselines — source review begun; implementation still required

Do not rename existing independent generation or tree mutation as EoH/FunSearch.
EoH couples heuristic descriptions with executable implementations, and its official
repository includes online bin packing. Pin the original release/commit and audit its
initialization, population management, operator prompts, parent sampling and replacement
rules before an adapter is called faithful. [EoH paper](https://arxiv.org/abs/2401.02051),
[author implementation](https://github.com/FeiLiu36/EoH).

FunSearch's released database maintains islands, groups programs by per-test score
signatures, samples clusters with a temperature schedule, prefers shorter programs within
clusters, orders sampled functions in prompts, and resets weaker islands. Preserve and
test those mechanics; converting a time-based reset to a call-based reset is a documented
adaptation. [Official database implementation](https://github.com/google-deepmind/funsearch/blob/main/implementation/programs_database.py),
[default configuration](https://github.com/google-deepmind/funsearch/blob/main/implementation/config.py).

Use two labeled comparisons: a shared-grammar mechanism comparison, and native-language
reference implementations with appropriately isolated execution. Constraining Python-based
methods to this JSON grammar may materially weaken them; such ports are adaptations.
Record original source/license/commit, all deviations and deterministic upstream-versus-port
fixtures. Require trace agreement for selection, prompts, scores and replacement before use.

Match model/digest, training suite, stopping rules, wall-time envelope, call ceiling and
token ceiling; charge critic calls, invalid proposals, retries and evaluation work.
Report achieved resource use and candidate counts as well as ceilings. Include random
grammar search, untargeted search and retrieval-only controls. Preselect the primary strong
comparator from development evidence before freezing confirmation. Equal calls alone do
not imply equal cost or equal candidate opportunity.

## 5. Retrieval and novelty — still open

The four-note seed corpus is insufficient. Build separate records for search frameworks
and concrete packing mechanisms; include primary sources, exact versions, review scope,
mechanism summaries, applicability and source hashes. Keep the v1 corpus untouched.
FunSearch is an immediate missing framework record, but adding framework names alone
will not supply useful policy revisions.

Before measuring retrieval, have reviewers label a fixed query set independently of
the retriever and blind to candidate condition. Include paraphrases, equivalent mechanisms,
irrelevant queries and intentionally absent sources. Report precision@k, recall@k over
the labeled corpus, reciprocal rank, unsupported-citation rate and abstentions. Corpus
recall is not recall over all literature. Keep query-development examples separate from
the final labeled evaluation set; report uncertainty, corpus coverage and disagreements.

For training-screened candidates, prepare a dossier containing executable behavior,
equivalence certificates, closest source mechanisms and utility results. Two independent
reviewers assess it blind to condition, with adjudication of disagreements. The generating
model and another role using the same model do not constitute independent review.
Until that work is performed, use `novelty: unresolved`; do not count a new expression
as a new algorithm. Recruitment or publication has not been performed.

## 6. Confirmation — design gate, not yet frozen

Freeze only after representation, baseline fidelity and role decisions are settled.
All existing train/validation/test data are development evidence. A protocol freeze must
include hashes of code/configs, exact methods, hypotheses, primary comparator and metric,
candidate-selection/fallback rules, budgets, seed count, multiplicity adjustment, exclusions,
failure handling, stopping rules and a full analysis script tested on synthetic outcomes.

Recommended primary outcome: paired difference in bin count for the policy selected using
training data only, with a prespecified practical margin and interval. Distinguish the
end-to-end outcome (including fallback) from generated-policy performance. Search run/seed
is an independent algorithmic replicate; streams within a run are not independent runs.
Use pilot variance to simulate power over both run and stream variability, document the
assumptions and choose sample size before opening the holdout. Do not invent a seed count
from this single small calibration or claim that zero successes gives adequate power.

After the freeze, generate a fresh versioned holdout from a seed selected outside tuning,
save its hash and restrict generator/critic access. Evaluate once after all candidate
selection is complete. An inspected or iteratively reused split becomes development data
and requires a new confirmatory version. Publish all arms, failures, negative outcomes and
deviations. No fresh holdout has been generated or inspected in this work.

## Immediate continuation

The next concrete decision is representation versus proposal quality. Run a prospectively
bounded deeper training-only representation audit; in parallel as a workstream, complete
source-pinned EoH/FunSearch fidelity fixtures. Do not scale the failed Qwen 4B role setup
or repeatedly alter calibration thresholds. A defensible negative result and clear failure
localization are valuable research progress, even without a positive discovery result.
