# Local model pilot

Date: 2026-10-10. Phase 1 remains open. Local inference replaces cloud inference for current work; the historical Azure failures are preserved.

**Continuation:** The initial settings below describe the first smoke test. Use [refined-pilot-protocol.md](refined-pilot-protocol.md) and `configs/local_refined_pilot.json` with `--structured` for the current calibrated continuation. See [refinement-findings.md](refinement-findings.md) for results and probe limitations. Existing raw runs retain their original configurations.

## Observed hardware and installation

Read from the machine: AMD Ryzen 5 3600 (6 cores, 12 threads), approximately 48 GiB usable RAM, NVIDIA GTX 1050 Ti (4 GiB VRAM), approximately 33 GiB free disk at inspection, Ollama 0.40.2. Available RAM was approximately 35 GiB. No additional models were downloaded.

| Installed model | Quantization | Disk size (decimal) | Role |
|---|---|---:|---|
| Qwen 3.5 9B | Q4_K_M | 6.6 GB | First paired generator pilot |
| Qwen 3.5 4B | Q4_K_M | 3.3 GB | Subsequent throughput/size comparison |
| DeepSeek R1 8B | Q4_K_M | 5.2 GB | Later reasoning-condition experiment |
| Gemma 3 12B | Q4_K_M | 8.2 GB | Later independent-family replication |

The installed DeepSeek digest starts `6995872bfe4c` and reports family `qwen3`: it is the newer R1-0528-Qwen3-8B, not the older R1-Distill-Llama-8B. Short model names do not establish lineage or independence. See the [current Ollama model entry](https://ollama.com/library/deepseek-r1:8b). Gemma's [model entry](https://ollama.com/library/gemma3:12b) identifies the independent family and its separate terms. Do not download GPT-OSS 20B or Llama merely to fill proposed roles before calibration establishes a need.

## Experimental decision

Run one model at a time. Start Qwen 9B with 8,192 context tokens, at most 512 output tokens, six CPU threads, temperature 0.7, top-p 0.95, top-k 20, and thinking disabled. This policy-generation task has short inputs; a larger advertised context window offers no demonstrated benefit here. Initial observed placement was 74% CPU / 26% GPU, about 6.4 GB model runtime memory as reported by Ollama. Initial token generation was around 5 tokens/second; this is not a completed-run average.

Both arms receive the same model digest, settings, candidate allowances, token ceilings, generation seeds by attempt, prompt template, archive design, train/validation/test data, and evaluator. Only parent-selection weights change. Actual prompts can diverge as the archives evolve, so actual token use and time need not be identical. This isolates sparse targeting within the current QD search; it is not yet a comparison against a separate conventional-generation baseline or a full multi-agent OPENEND system.

The native [Ollama chat API](https://docs.ollama.com/api/chat) provides prompt/generated token counts and timing. `src/openend/local.py` connects only to `127.0.0.1:11434`, bypasses HTTP proxies, rejects remote-model metadata, and neither reads cloud credentials nor downloads models. It checks the installed digest before each request. Runtime errors have no automatic retries. Invalid/truncated candidates consume attempts; no free repairs. The existing bounded policy interpreter and independent evaluator remain authoritative.

Generation seeds improve repeatability but do not guarantee bit-identical fresh GPU inference. Replaying saved candidates verifies their objective scores without model calls. Equal token allowances across different tokenizers would not imply equal compute; cross-family runs are separate within-model replications.

```powershell
.venv\Scripts\openend.exe run --config configs/local_pilot.json --backend local --model qwen3.5:9b --output results/raw/local-qwen35-9b-v1
.venv\Scripts\openend.exe verify results/raw/local-qwen35-9b-v1
.venv\Scripts\openend.exe replay results/raw/local-qwen35-9b-v1
```

Always use a new output directory. The first local pilot is three paired seeds and four attempts per arm (24 attempts). This is a feasibility/calibration study on the previously inspected development benchmark. It cannot provide confirmatory evidence, independently verified novelty, or statistical generality. Roles such as critic and hypothesis tester remain proposed interventions to evaluate later, not established model abilities.
