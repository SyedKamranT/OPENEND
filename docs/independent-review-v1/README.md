# Independent review packet v1 — awaiting reviewers

Prepared 2026-10-13. No reviews have been performed or attributed to anyone.
This packet supports the independent novelty/retrieval requirement in
`docs/research-question.md`; an agent cannot self-certify independence.

Two reviewers with algorithm-design/bin-packing expertise should work separately before
adjudication. Record conflicts and whether either reviewer designed these candidates,
authored the corpus notes, or saw the development retrieval scores. Decline an independence
attestation when those conditions prevent independent review. This packet is a technical
audit, not the deferred blinded participant preference study (H5). Determine applicable
institutional requirements before recruiting human participants.

## Material for reviewers

- `cases.json`: anonymous mechanism cases, expression language contract and fixed states.
- `../../data/corpus/frozen-packing-notes-v2.json`: frozen source leads with provenance.
- `review-template.json`: blank structured response; preserve the packet hash.
- Primary sources linked in the corpus. Notes do not replace source verification.

Do not send `maintainer-key.json` to reviewers. It identifies deliberately included
reference controls and source provenance. Repository separation is administrative only;
this folder is not an access-control mechanism. If the key is inspected, disclose it.

## Candidate task

For every case, inspect executable behavior, look for equivalent mechanisms, and return
one of: `known_reference`, `known_other`, `no_equivalent_found_in_scope`, `unresolved`.
Provide mechanism reasoning and checked primary-source URLs. Record what you searched,
including databases/queries/dates, and the scope limits. `no_equivalent_found_in_scope`
requires completed documented search; it is never a universal novelty certification.
Both known verdicts require evidence; insufficient coverage should yield `unresolved`.
No case is presented as a utility-successful discovery. Review mechanism identity
without candidate condition labels or quality rankings.

## Retrieval task

Independently author at least 12 new queries before viewing any system retrieval output:
eight answerable from this corpus and four absent-topic or unsupported-mechanism queries.
Include paraphrases rather than copying note titles. For each query, label all relevant
record IDs with source-based reasoning; use an empty list only when no source record is
relevant. The other reviewer should label that query set independently, then disagreements
are adjudicated before freezing final qrels. Preserve both original labels.

The existing 12 development queries must not serve as this new evaluation set. The same
author produced their queries and labels; their observed recall is not independent evidence.
Freeze the independent query/label file and hashes before a new evaluation is executed.
Report query coverage and absent-query false retrieval, not only hit rates.

## Return and adjudication

Each reviewer supplies a completed JSON file separately. Keep reviewer IDs pseudonymous;
do not add emails or personal contact details to public artifacts. A maintainer checks
completeness without changing the judgments. Disagreements require a recorded independent
adjudicator or a documented unresolved verdict. Agreement alone is not proof of correctness.
Final labels remain pending until primary evidence and declared scope can be audited.

No invitation, email or other outreach has been sent. Providing these files does not
authorize anyone to represent model-generated judgments as independent human review.
