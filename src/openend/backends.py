"""Offline mutation and an explicitly requested, budgeted Responses API backend."""

import os
from dataclasses import dataclass
from urllib.parse import urlsplit

from .artifacts import canonical
from .policy import FEATURES, mutate

SYSTEM_PROMPT = """Design a bin-scoring heuristic for online bin packing (capacity 100).
Return only a JSON object with exactly one field: expression. No Python, prose, or code fences.
The host places each arriving item in the feasible existing bin with maximum score, with
earliest-bin tie breaks. A new bin is opened only if no existing bin is feasible.
You cannot see future items. All features are bounded in [0,1]: gap=(remaining-item)/100,
remaining=remaining/100, item=item/100, index=bin_index/max(1,bin_count-1),
fraction=item/remaining, exact_fit=1 if remaining==item else 0.
An expression is a feature string, a number in [-10,10], or an operator array:
[add,a,b], [sub,a,b], [mul,a,b], [div,a,b], [min,a,b], [max,a,b], [abs,a], [neg,a].
Use quoted operator strings in JSON. Division returns 0 when |denominator|<0.000001.
Intermediate scores are clipped to [-1000000,1000000]. Maximum 31 nodes, depth 6.
Improve the given parent using a nontrivial small variation. Aim to minimize bins across
uniform, bimodal, complementary-pair, and three-partition item streams. Parent fitness is
mean(volume/count lower bound divided by bins used), higher is better.
"""


def prompt_for(parent, fitness):
    return canonical(
        {"parent": parent.to_object(), "training_fitness": round(fitness, 8), "features": FEATURES}
    )


@dataclass
class Proposal:
    text: str | None
    usage: dict
    metadata: dict
    status: str = "ok"


class OfflineBackend:
    kind = "offline"

    def identity(self):
        return {
            "kind": self.kind,
            "model": "seeded-tree-mutation-v1",
            "api_calls": False,
            "system_prompt": SYSTEM_PROMPT,
        }

    def reservation(self, prompt):
        return 0

    def propose(self, parent, fitness, rng):
        return Proposal(
            mutate(parent, rng),
            {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            {"model": "seeded-tree-mutation-v1"},
        )


def settings(env_path):
    # Local .env is read only on explicit API/doctor commands. Never log its contents.
    from dotenv import dotenv_values

    values = dotenv_values(env_path, interpolate=False)
    names = ("LLM_API_KEY", "LLM_MODEL", "LLM_BASE_URL", "LLM_MAX_TOKENS", "LLM_TEMPERATURE")
    return {name: os.environ.get(name, values.get(name)) for name in names}


class APIBackend:
    kind = "api"

    def __init__(self, env_path, max_output_tokens, reasoning_effort="none"):
        from openai import OpenAI

        cfg = settings(env_path)
        if not all(cfg.get(k) for k in ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL")):
            raise ValueError("LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL must be configured")
        url = urlsplit(cfg["LLM_BASE_URL"])
        if url.scheme != "https" or url.username or url.password or url.query or url.fragment:
            raise ValueError("LLM_BASE_URL must be HTTPS without credentials, query, or fragment")
        self.model = cfg["LLM_MODEL"]
        self.api_key = cfg["LLM_API_KEY"]
        self.host = url.hostname
        self.max_output = min(
            max_output_tokens, int(cfg.get("LLM_MAX_TOKENS") or max_output_tokens)
        )
        if not 16 <= self.max_output <= 8192:
            raise ValueError("LLM_MAX_TOKENS must be between 16 and 8192")
        self.reasoning_effort = reasoning_effort
        self.terminal_error = None
        self.temperature = float(cfg["LLM_TEMPERATURE"]) if cfg.get("LLM_TEMPERATURE") else None
        if self.temperature is not None and not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        # Azure API-key authentication uses api-key; bearer-only requests can be rejected.
        headers = {"api-key": self.api_key} if self.host.endswith(".openai.azure.com") else {}
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=cfg["LLM_BASE_URL"].rstrip("/") + "/",
            default_headers=headers,
            max_retries=0,
            timeout=45,
        )

    def identity(self):
        return {
            "kind": self.kind,
            "model": self.model,
            "endpoint_host": self.host,
            "max_output_tokens": self.max_output,
            "temperature": self.temperature,
            "reasoning_effort": self.reasoning_effort,
            "max_retries": 0,
            "system_prompt": SYSTEM_PROMPT,
        }

    def reservation(self, prompt):
        # Conservative byte-based estimate, NOT a provider-guaranteed tokenizer count.
        # Usage is reconciled after each response; overshoots invalidate budget parity.
        return len((SYSTEM_PROMPT + prompt).encode("utf-8")) + 512 + self.max_output

    def propose(self, parent, fitness, rng):
        if self.terminal_error is not None:
            return Proposal(None, {}, {**self.terminal_error, "request_sent": False}, "api_error")
        from openai import OpenAIError

        prompt = prompt_for(parent, fitness)
        request = {
            "model": self.model,
            "instructions": SYSTEM_PROMPT,
            "input": prompt,
            "max_output_tokens": self.max_output,
            "store": False,
            "reasoning": {"effort": self.reasoning_effort},
            "text": {"format": {"type": "json_object"}},
        }
        if self.temperature is not None:
            request["temperature"] = self.temperature
        try:
            response = self.client.responses.create(**request)
        except OpenAIError as exc:
            # Exception bodies/headers may contain credentials. Retain only safe diagnostics.
            self.terminal_error = {
                "error_type": type(exc).__name__,
                "http_status": getattr(exc, "status_code", None),
            }
            return Proposal(None, {}, {**self.terminal_error, "request_sent": True}, "api_error")
        usage = response.usage.model_dump() if response.usage is not None else {}
        metadata = {
            "model": response.model,
            "response_id": response.id,
            "response_status": response.status,
            "incomplete_details": (
                response.incomplete_details.model_dump() if response.incomplete_details else None
            ),
        }
        text = response.output_text.replace(self.api_key, "[REDACTED]")
        status = "ok" if response.status == "completed" else "incomplete_response"
        if not usage or any(
            type(usage.get(k)) is not int or usage[k] < 0
            for k in ("input_tokens", "output_tokens", "total_tokens")
        ):
            status = "missing_usage"
        return Proposal(text, usage, metadata, status)
