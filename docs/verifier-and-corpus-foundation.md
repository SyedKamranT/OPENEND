# Verifier and retrieval foundations

Date: 2026-10-10. These are incomplete components toward the full goal, separate from the running v3 experiment.

## Complete-domain reference equivalence

`src/openend/equivalence.py` certifies a sufficient class of equivalences to the three frozen implemented reference policies. For policies without the `index` feature, it evaluates all 5,050 feasible integer `(item, remaining)` pairs at capacity 100 using the actual bounded interpreter. Per-item scores that are constant reproduce first-fit; strictly descending scores reproduce best-fit; strictly ascending scores reproduce worst-fit. Equal remaining capacities have equal scores, and the host's earliest-bin tie rule is shared. The argument therefore covers arbitrary bin lists under this restricted contract, not only a sampled probe panel.

Index dependence, non-monotone scores, and other unsupported cases return unresolved. Protected division, floating-point absorption, and intermediate clipping are tested; the checker does not use a real-arithmetic simplification that could disagree with the interpreter. The interpreter remains a shared dependency, and the certificate says nothing about other capacities or item types.

The posthoc v2 audits identify reference equivalents among **11/43 unique Qwen policies** and **9/22 unique Gemma policies**. Certificates, score-table hashes, verifier/interpreter hashes, and original run-manifest hashes are in `results/tables/qwen-v2-equivalence.json` and `results/tables/gemma-v2-equivalence.json`. Existing experiment labels and artifacts are unchanged. This is useful known-mechanism rejection, not a measured literature-wide novelty verifier or independent expert adjudication.

```powershell
.venv\Scripts\python.exe -m openend.equivalence results/raw/local-qwen35-9b-refined-v2 --output results/tables/NEW_AUDIT.json
```

## Frozen source-note corpus

`data/corpus/frozen-review-notes-v1.json` freezes four original review notes, with versioned primary-source citations, evidence scopes, review dates, document hashes, and an overall content hash. It does **not** contain complete papers. The primary abstracts were checked on 2026-10-10:

- [ELM](https://arxiv.org/abs/2206.08896v1): code-model mutation and a MAP-Elites experiment.
- [EoH](https://arxiv.org/abs/2401.02051v3): jointly evolved heuristic descriptions/programs, including reported online bin-packing results.
- [AlphaEvolve](https://arxiv.org/abs/2506.13131v1): evaluator-guided evolutionary code editing.
- [MAP-Elites](https://arxiv.org/abs/1504.04909v1): retaining high-quality solutions along chosen descriptive dimensions.

The Nature FunSearch page failed retrieval during this step; no newly verified FunSearch note was silently fabricated. It remains in the broader existing literature map and needs a retrievable primary source for corpus expansion.

`src/openend/corpus.py` supplies deterministic local BM25 retrieval with citation IDs and document hashes. Snapshot creation refuses overwriting, and loading checks content integrity. Local hashes are tamper-evident relative to their manifest, not an externally signed timestamp or immutable external archive. A keyword smoke query for online bin-packing heuristic evolution ranks EoH first. Tests cover integrity, stable freezing independent of input order, citation preservation, duplicate IDs, and no-hit abstention.

```powershell
.venv\Scripts\python.exe -m openend.corpus search data/corpus/frozen-review-notes-v1.json --query "online bin packing heuristic evolution" --top-k 2
```

Retrieval recall/precision on independently labeled queries is **unmeasured**. A matching note is a source lead rather than proof that two mechanisms are equivalent; no hit never establishes novelty. This four-note seed lacks the coverage and algorithm details needed for a discovery claim. Expand lawful source evidence, evaluate retrieval and adversarial verification, then integrate them into budgeted agent roles and baseline conditions. None of these notes or certificates was injected into the frozen v3 generator.
