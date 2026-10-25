# OPENEND internal technical review and development decisions

Date: 2026-10-14. Reviewer: Codex, the same AI assistant involved in implementation
and research planning. **Internal self-review; not independent peer review.**

The user has asked to defer external review and continue using this review to guide
work. This document supplies that development review. It does not fill the independent
review templates, authenticate the Gemini model identity, or create novelty labels.
External review is deferred, not rejected or recorded as complete.

## Recommendation

**Proceed with development; major revisions remain before a confirmatory research lock.**
The project has a bounded evaluator, useful failure diagnostics and replayable evidence.
Its strongest current result is failure localization: shallow representation search was
insufficient, a deeper search found a small training improvement, critic/target gates
failed under the tested settings, and baseline adapters produced valid but unimproved
policies. These findings justify better experiments. They do not establish discovery
superiority, historical novelty, or the usefulness of sparse targeting.

Independent review need not block implementation, training-only experiments or analysis
development. It remains necessary for the independently validated discovery claim in
H4 under the current specification. A later reviewer may require changes that make an
earlier experiment exploratory; postponing review cannot guarantee retrospective approval.

This review inspected the research question, hypotheses, pilot/upgrade protocols, closure
audit, baseline state and retrieval evaluation code, baseline fidelity/results documents,
and prior diagnostic reports. It is not a line-by-line audit of the entire repository.
The last recorded suite result is 103 passing tests and clean Ruff on 2026-10-13; tests
were not rerun merely to write this document. Tests support engineering correctness,
not scientific validity or source-implementation equivalence beyond their fixtures.

## 1. What is the question, and can the proposed contribution be novel?

**Answer:** the question is testable, but the contribution is not yet established.
Evolutionary LLM heuristic design, evaluator-guided program search, and retaining elites
across behavioral dimensions are established ideas. The project cannot claim originality
from combining these components. See the primary [EoH paper](https://arxiv.org/abs/2401.02051),
[FunSearch paper](https://www.nature.com/articles/s41586-023-06924-6), and
[MAP-Elites paper](https://arxiv.org/abs/1504.04909). These sources establish relevant
precedents, not an exhaustive literature-gap review.

The immediate defensible question is:

> With a fixed model, evaluator, grammar, archive and resource allowance, does weighting
> parent selection by behavioral distance from fixed reference heuristics improve the
> packing performance of training-selected outputs relative to uniform parent selection?

The eventual H4 question is different: does that intervention increase distinct,
independently verified corpus-novel and utility-successful mechanisms per allowance?
Keep these questions separate. A positive utility result would not establish H4.

**Major finding R1:** current sparsity is distance from fixed reference signatures.
It is not an estimate of how often a behavioral region has been explored, and it does
not by itself instruct a generator to reach a target cell. Call this treatment
**reference-distance parent weighting** in the next protocol. Dynamic archive occupancy
weighting and explicit target-conditioned generation require separate interventions.
Do not describe the existing experiment as isolating all three mechanisms.

**Required question:** what remains distinctive after controlling for ordinary diversity
search, random variation and the representation? **Current answer:** unresolved; use
matched ablations to test the marginal contribution rather than assert it in advance.

## 2. Are the six reviewed cases new mechanisms?

**Answer:** five are reference-equivalent under the integer capacity-100 contract;
the sixth has unresolved novelty. Cases 01/04 implement First Fit, 03/05 Best Fit,
and 06 Worst Fit. The [model-audit validation](independent-review-v1/model-audit-gemini-v1-validation.md)
checks 18 traces and 25,250 feasible score states across those controls.

For case 02, exact arithmetic gives `max(item² - gap, 0)`. If any feasible score is
positive, the policy favors the smallest gap; when all scores are zero, it picks the
earliest feasible bin. The implementation uses floating point: the original and an
algebraically simplified expression obtained different training totals. Algebraic
equivalence must not silently become executable equivalence.

**Major finding R2:** the maintainer key records case origins, not novelty ground truth.
The Gemini audit supplies 5/5 reference-control agreement, not 6/6 novelty accuracy.
An absence claim over eleven notes cannot establish absence from classical literature.
Preserve the original model judgments and their separate validation; do not replace
their unresolved status with this self-review.

**Development decision:** retain the current float interpreter for existing experiments;
use exact-rational evaluation as a sensitivity diagnostic. Any numerical-semantics change
gets a new evaluator version and symmetric evaluation of every affected comparator.
Keep syntax duplicates, finite behavioral duplicates, demonstrated equivalence and
literature novelty as separate fields. Finite matching probes do not prove equivalence.

## 3. Can the policy language express useful improvements?

**Answer:** a small improvement exists on training data; practically meaningful utility
and generalization remain unestablished. The shallow audit tested 1,053 policies without
improvement. The deeper bounded audit found 1,475 bins versus Best Fit's 1,476, an
approximately 0.068% reduction, below the provisional 1% utility screen.
See [representation results](representation-v2-results.md).

The grammar lacks general aggregate bin information, cross-bin score operations and
stateful class management. The host also cannot voluntarily open a new bin while another
is feasible. These restrictions can exclude mechanisms used by relevant native methods.
Failure to find a 1% improvement does not distinguish search weakness from a restrictive
language, difficult benchmark or insufficient budget.

**Required question:** should we expand the representation? **Current answer:** investigate
missing information using training-only diagnostics first. A richer language must be
versioned, justified by a concrete missing mechanism, and shared across applicable arms.
Do not modify it using fresh holdout outcomes. The known witness is a diagnostic positive
control, not a candidate independently discovered by a model that has been shown it.

## 4. Are critic feedback and target control reliable enough?

**Answer:** not under the tested calibration. Grounded Qwen 4B scored 1/3 accepted critic
responses, 0/3 target-only hits and 1/3 supplied-witness hits. The gates failed; the small
case bank cannot support a claim about all models or all prompts. See
[grounded calibration results](grounded-calibration-v2-results.md).

**Development decision:** the next parent-weighting comparison should omit critic and
explicit target roles symmetrically. This isolates the treatment actually implemented
and avoids adding failed components to the primary causal contrast. It does not erase
their negative calibration results. Study a host-evaluated revision role separately:
the model proposes, the interpreter supplies consequences, and unsupported prose never
becomes trusted feedback. Freeze a larger training-only bank before any retest, covering
ties, no feasible bins, protected division, saturation and non-reference policies.

**Required question:** can generation copy a known witness before being expected to reach
an unspecified useful region? **Current answer:** the existing witness-control result
does not establish this. Keep imitation, targeting and usefulness as distinct gates.

## 5. Are EoH and FunSearch fair, strong baselines?

**Answer:** they are relevant comparison targets; the present implementations are JSON
adaptations, not faithful native reproductions. Pinned upstream source and differential
primitive tests are good foundations. They do not validate all prompts, stochastic
sampling, initialization, parsing retries, island resets or representation changes.

The [adapter trial](baseline-adapters-v1-results.md) completed 24 responses each for EoH
and FunSearch adaptations, then stopped after five independent-generation responses and
one unresolved request. Both complete arms tied Best Fit. One seed and an incomplete
comparison do not establish relative efficacy or equivalence.

**Development decisions:**

- Preserve this trial as interrupted; do not stitch new responses into its original
  journal or pretend the unresolved request used zero resources.
- Before another live adapter trial, write a prospective replacement protocol with
  fixed budgets and failure rules. Rerun all arms symmetrically in a new directory;
  retain the old trial and include its known and unknown resource use in the record.
- Keep shared-grammar comparisons and native-method reproductions separately labeled.
  Until a verified containment environment exists, do not execute model-written Python
  in a plain subprocess and call that secure isolation.
- Use shared model/digest, data access, stopping rules and explicit call/token ceilings.
  Record evaluation work and runtime too. Equal ceilings are opportunities, not proof
  of equal consumption. Method-specific prompt overhead is part of the method's cost.

**Required question:** which comparator answers which claim? **Answer:** uniform parent
selection isolates the weighting intervention; independent generation and grammar search
check search overhead; EoH/FunSearch comparisons assess competitiveness. Select a primary
contrast before confirmation. Do not pick the weakest baseline after viewing outcomes.

## 6. Is retrieval validated, and is the literature coverage sufficient?

**Answer:** not yet. Eleven frozen leads improve the original four-note corpus, but
still provide limited coverage. Same-author development recall@3 rose from 0.3 to 1.0
on ten answerable queries; both absent queries returned irrelevant matches. High recall
on this set does not establish reliable novelty detection or good abstention.

The Gemini audit contributes twelve provisional queries, eight answerable and four
absent. They have not been independently cross-labeled or evaluated. Keep them unscored
for now. Relevance ambiguities include OR versus Weibull scope, partial operator matches,
and omitted alternative relevant records. Do not resolve these by looking at retrieved
rankings and changing labels until scores improve.

**Development decisions:** separate corpus coverage from ranking quality; report recall
and reciprocal rank on answerable queries, precision with its denominator, and false
retrieval/abstention on absent queries. Treat retrieved sources as leads requiring
inspection. Develop rejection thresholds only on development queries, then freeze them.
No-hit retrieval means insufficient evidence, not a positive novelty verdict.

**Required question:** what sources are missing? **Current answer:** perform a documented
search for predecessor bin-scoring heuristics, automated heuristic design, novelty/diversity
selection and later close methods, with forward/backward citation searches. Record exact
queries, dates, inspected primary passages, exclusions and scope. This self-review has
not completed that search and cannot certify a literature gap.

## 7. What should the primary outcome and analysis be?

**Major finding R3:** H4 specifies validated discovery yield as the eventual primary
outcome, while the upgrade plan recommends a utility outcome. These can coexist only
as explicitly distinct studies. Do not silently replace an unmeasurable primary metric
with an easier proxy after outcomes are known.

**Development decision:** prepare a separately named utility study while H4 remains
pending independent labels. For a paired search replicate r and a common evaluation
suite, define `D_r = B_uniform,r - B_weighted,r`, where B is total bins used by the
training-selected policy. Positive D favors weighting. Specify either equal-weighted
family means or a fixed aggregate suite as the target before collecting confirmation;
do not switch aggregation after seeing which is favorable.

Training alone selects candidates, with deterministic tie rules and a predeclared
reference fallback. Report the end-to-end selected-policy outcome, fallback rate and
best generated-policy outcome separately. The best-fit reference is not a newly generated
discovery. Use the same utility and failure screens in every arm.

The independent algorithmic replicate is the search run, paired across methods by the
declared seed and benchmark block. Candidates from one evolving archive are dependent.
Repeated runs on one fixed suite estimate search variability conditional on that suite;
they do not establish generalization across tasks. Shared holdout streams also induce
dependence across runs. A broader generalization claim needs independently generated
benchmark blocks and an analysis respecting both block and run structure.

**Required question:** how many runs and streams are enough? **Answer:** not determined
by present evidence. Build a synthetic-outcome analysis test and sensitivity simulation
before choosing sample size. Vary run variability, stream/block variability, zero-gain
mass, between-arm correlation and failure probability. Declare precision/power targets
and a meaningful margin, then show feasibility under the chosen budget. Zero variance
from repeated fallback outputs is not evidence that a tiny sample is sufficient.

The existing 1% gain and 5% family-regression limits are provisional practical screens,
not significance thresholds or justified universal margins. Keep them unchanged for
development comparisons; any confirmatory replacement needs a prospective rationale.
Predeclare whether a family constraint applies to observed totals or inferential bounds.
Keep one primary contrast; label other contrasts exploratory or define multiplicity
control before unblinding. A nonsignificant result is not equivalence.

## 8. How do we handle failures and the fresh holdout?

**Answer:** retain failures as outcomes and preserve the confirmation boundary.
Invalid candidate attempts are charged and retained; training selection can use the
declared fallback. An interrupted condition with unknown usage is a different problem:
it cannot simply be treated as a completed no-improvement run or silently excluded.
Predeclare the failed-pair reporting, replacement and sensitivity rules before new runs.

All inspected splits are development data. Freeze model, prompts, grammar, evaluator,
archive, references, corpus, selection rules, budgets, run/block counts, primary contrast,
analysis and failure rules before generating or opening a fresh confirmatory holdout.
Hash the frozen package. Complete and hash all training-selected policies before their
holdout evaluation. Keep holdout inputs and results out of generator and critic access.
Use an independent custodian or a documented access-controlled process; a public fixed
seed is reproducible but does not provide independent custody.

**Required question:** can expert review happen at the end? **Answer:** it can be deferred
for development, as requested. For final novelty adjudication, preserve blinded candidate
IDs and condition-hidden dossiers. For confirmatory design review, obtain review before
unblinding final outcomes where feasible. Post-outcome design changes cannot retrospectively
be called preregistered, and altered claims may require another untouched holdout.

## 9. Can source code remain private?

**Answer:** yes for the proposed methods/evidence review, with a stated limitation.
Provide the complete scoring contract, anonymous expressions, traces, source passages,
protocol, resource accounting, uncertainty analysis and deviation history. A reviewer
without code can critique these artifacts but cannot certify implementation correctness
or full reproduction. A code hash identifies a version; it does not expose its behavior
for inspection. Keep the distinction in any eventual manuscript or review summary.

The authoring agent is not an independent reviewer. Gemini is one external model audit
with declared limitations. Neither can be counted as two human expert reviews. This does
not prevent implementation progress and does not require asking for permission again.

## 10. Work order and acceptance criteria

| Order | Work we can do now | Evidence required to call that item done |
|---|---|---|
| 1 | Reconcile treatment terminology and separate utility-study/H4 outcomes | One versioned protocol names the implemented intervention and one primary estimand |
| 2 | Build synthetic analysis and sample-size sensitivity tooling | Known null/effect/failure scenarios checked; assumptions and feasible design recorded |
| 3 | Complete adapter fidelity fixtures and replacement protocol | Source-linked deviation matrix, state/prompt fixtures, fixed budget and interruption rules |
| 4 | Complete a bounded training-only engineering comparison | Every request accounted; saved-response replay; no efficacy interpretation of an incomplete pair |
| 5 | Expand mechanism-level source coverage and develop abstention | Reproducible search log, frozen corpus versions, development-only diagnostics |
| 6 | Prepare final blind dossiers and protocol freeze candidate | Selection, duplicate handling, candidate IDs, source/config hashes and analysis fixed |
| Deferred | Obtain external technical review and independent qrels/novelty labels | Actual separate assessments, declared conflicts, source evidence and recorded adjudication |
| Later gate | Run confirmatory evaluation | Frozen design, fresh controlled holdout, complete failure accounting, no unreported retuning |

No optional model role is required to pass before a simpler, explicitly scoped study can
proceed. No positive scientific result is required either. A well-bounded negative result
can be useful. The immediate authorization is to continue development using these decisions;
the research lock remains open for the listed substantive reasons, not merely for a
missing approval signature.

## Disposition of the earlier review questions

| Question | Current review answer |
|---|---|
| Meaningful novelty beyond established search methods? | Plausible narrow question; contribution and literature gap unestablished |
| Different expression or different mechanism? | Five demonstrated controls; witness novelty unresolved and numerically sensitive |
| Sufficient retrieval validation? | Development evidence only; independent labels and abstention work pending |
| Fair strong baselines? | Transparent JSON adaptations; native fidelity and complete comparison pending |
| Adequate experimental design? | Good engineering controls; primary-study distinction, precision design and fresh holdout still needed |
| Permission to continue implementation? | Proceed under the user's instruction; external review deferred |
| Does this close Phase 1 or validate H4? | No; use it as an internal decision record and work plan |
