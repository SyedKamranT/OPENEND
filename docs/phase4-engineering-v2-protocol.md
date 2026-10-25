# Phase 4 local adapted-baseline engineering v2

Frozen before execution, 2026-10-16. Engineering only; not useful-signal or superiority evidence.
Three arms: independent, eoh_json, funsearch_json. Same 48 training streams, production
finite grammar and host. One seed 20261016; shuffled method order determined by the
existing runner. Per arm: 24 calls, 60000 accounted tokens, 128 output tokens per call;
context 8192. EoH population 4, FunSearch islands 4, reset every 12 attempts. Thus EoH
can complete initialization and one cycle of four operators if all calls are admitted.
Short output cap tests transport/accounting; it may differentially constrain EoH thoughts.
No effectiveness ranking is justified by this small engineering run.

Local qwen3.5:4b digest d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04,
Ollama 0.40.2, think=false; temperature .7, top_p .95, top_k 20, repeat penalty 1,
presence penalty 0, six threads. Verify identity before execution. No downloads/cloud.
No retries, budget extensions or outcome-dependent replacements. Started calls journaled;
invalid/incomplete responses count. Fatal transport/identity/usage errors stop remaining
arms; retain missing outcomes, never report missing arms as zero. API request timeout
600 seconds. Existing interrupted v1 artifacts remain unchanged. No evaluation splits.

Run snapshots this protocol, config, source, model metadata, requests, responses and states.
Accept engineering completion only if all 72 attempts are accounted and offline replay
matches. Distinguish valid-response yield from completion and usefulness. Native Python
reproduction is a separate outstanding obligation, not satisfied by this run.
