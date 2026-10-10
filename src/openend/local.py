"""Local-only Ollama transport; no credentials, cloud fallback, or implicit downloads."""

import json
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

from .backends import SYSTEM_PROMPT, Proposal, prompt_for
from .grammar import GRAMMAR_INSTRUCTIONS, policy_schema


class LocalBackend:
    kind = "local"

    def __init__(self, model, max_output_tokens, context=8192, structured=False):
        self.model = model
        self.max_output = max_output_tokens
        self.context = context
        self.output_format = policy_schema() if structured else "json"
        self.system_prompt = SYSTEM_PROMPT + (GRAMMAR_INSTRUCTIONS if structured else "")
        self.terminal_error = None
        self.opener = build_opener(ProxyHandler({}))
        self.version = self._request("version")["version"]
        self.record = self._model_record()
        if self.record.get("remote_host") or self.record.get("remote_model"):
            raise ValueError("cloud models are forbidden in local mode")
        self.show = self._request("show", {"model": model})
        if self.show.get("remote_host") or self.show.get("remote_model"):
            raise ValueError("cloud models are forbidden in local mode")
        self.options = {
            "num_ctx": context,
            "num_predict": max_output_tokens,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 20,
            "repeat_penalty": 1.0,
            "presence_penalty": 0.0,
            "num_thread": 6,
        }

    def _request(self, route, payload=None):
        body = json.dumps(payload).encode() if payload is not None else None
        request = Request(
            "http://127.0.0.1:11434/api/" + route,
            body,
            {"Content-Type": "application/json"},
        )
        with self.opener.open(request, timeout=600) as response:
            return json.load(response)

    def _model_record(self):
        records = self._request("tags")["models"]
        for record in records:
            if record["name"] == self.model:
                return record
        raise ValueError("requested model must already be installed locally")

    def identity(self):
        return {
            "kind": self.kind,
            "model": self.model,
            "model_digest": self.record["digest"],
            "details": self.record["details"],
            "ollama_version": self.version,
            "options": self.options,
            "think": False,
            "format": self.output_format,
            "endpoint_host": "127.0.0.1",
            "cloud_calls": False,
            "max_retries": 0,
            "system_prompt": self.system_prompt,
        }

    def reservation(self, prompt):
        return len((self.system_prompt + prompt).encode()) + 512 + self.max_output

    def propose(self, parent, fitness, rng):
        if self.terminal_error:
            return Proposal(None, {}, {**self.terminal_error, "request_sent": False}, "api_error")
        prompt = prompt_for(parent, fitness)
        if self.reservation(prompt) > self.context:
            return Proposal(None, {}, {"error_type": "ContextReservationExceeded"}, "api_error")
        seed = rng.randrange(2**31)
        started = time.monotonic()
        try:
            if self._model_record()["digest"] != self.record["digest"]:
                self.terminal_error = {"error_type": "ModelDigestChanged"}
                return Proposal(None, {}, self.terminal_error, "model_changed")
            response = self._request(
                "chat",
                {
                    "model": self.model,
                    "stream": False,
                    "think": False,
                    "format": self.output_format,
                    "keep_alive": "10m",
                    "options": {**self.options, "seed": seed},
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
        except (URLError, OSError, ValueError) as exc:
            self.terminal_error = {"error_type": type(exc).__name__}
            return Proposal(None, {}, {**self.terminal_error, "request_sent": True}, "api_error")
        counts = [response.get("prompt_eval_count"), response.get("eval_count")]
        usage = {}
        if all(type(n) is int and n >= 0 for n in counts):
            usage = {
                "input_tokens": counts[0],
                "output_tokens": counts[1],
                "total_tokens": sum(counts),
            }
        status = (
            "ok"
            if response.get("done") and response.get("done_reason") == "stop"
            else "incomplete_response"
        )
        if not usage:
            status = "missing_usage"
        if response.get("model") != self.model:
            status = "model_changed"
        metadata = {
            "model": self.model + "@" + self.record["digest"],
            "seed": seed,
            "done_reason": response.get("done_reason"),
            "wall_seconds": time.monotonic() - started,
            "request_sent": True,
            **{
                k: response.get(k)
                for k in (
                    "total_duration",
                    "load_duration",
                    "prompt_eval_duration",
                    "eval_duration",
                )
            },
        }
        return Proposal(response.get("message", {}).get("content", ""), usage, metadata, status)
