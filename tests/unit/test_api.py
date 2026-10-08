import json
import random
from types import SimpleNamespace

import pytest

from openend.backends import APIBackend
from openend.policy import REFERENCES


def make_backend(tmp_path, monkeypatch, create):
    captured = {}
    for name in ("LLM_API_KEY", "LLM_MODEL", "LLM_BASE_URL", "LLM_MAX_TOKENS", "LLM_TEMPERATURE"):
        monkeypatch.delenv(name, raising=False)
    env = tmp_path / ".env"
    env.write_text(
        "LLM_API_KEY=unit-test-only-secret\nLLM_MODEL=test-deployment\n"
        "LLM_BASE_URL=https://example.openai.azure.com/openai/v1\n"
        "LLM_MAX_TOKENS=512\nLLM_TEMPERATURE=\n"
    )

    def client(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(responses=SimpleNamespace(create=create))

    monkeypatch.setattr("openai.OpenAI", client)
    return APIBackend(env, 2048), captured


def test_api_respects_env_cap_azure_auth_usage_and_secret_redaction(tmp_path, monkeypatch):
    sent = {}

    def create(**kwargs):
        sent.update(kwargs)
        return SimpleNamespace(
            model="test-deployment-2026",
            id="response-test",
            status="completed",
            incomplete_details=None,
            output_text='{"expression":0} unit-test-only-secret',
            usage=SimpleNamespace(
                model_dump=lambda: {
                    "input_tokens": 100,
                    "output_tokens": 30,
                    "total_tokens": 130,
                    "output_tokens_details": {"reasoning_tokens": 10},
                }
            ),
        )

    backend, client = make_backend(tmp_path, monkeypatch, create)
    result = backend.propose(REFERENCES["best_fit"], 0.9, random.Random(0))
    assert client["default_headers"]["api-key"] == "unit-test-only-secret"
    assert client["max_retries"] == 0
    assert sent["max_output_tokens"] == 512
    assert sent["store"] is False
    assert "temperature" not in sent
    assert result.usage["total_tokens"] == 130
    assert result.usage["output_tokens_details"]["reasoning_tokens"] == 10
    assert "unit-test-only-secret" not in json.dumps(backend.identity()) + result.text + str(sent)


def test_terminal_api_error_is_sanitized_and_disables_later_calls(tmp_path, monkeypatch):
    from openai import OpenAIError

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        raise OpenAIError("secret=unit-test-only-secret should never be logged")

    backend, _ = make_backend(tmp_path, monkeypatch, create)
    first = backend.propose(REFERENCES["best_fit"], 1.0, random.Random(0))
    second = backend.propose(REFERENCES["best_fit"], 1.0, random.Random(0))
    assert len(calls) == 1
    assert first.metadata["request_sent"] is True
    assert second.metadata["request_sent"] is False
    assert "unit-test-only-secret" not in str(first.metadata)


def test_unknown_usage_does_not_become_free_generation(tmp_path, monkeypatch):
    def create(**kwargs):
        return SimpleNamespace(
            model="m",
            id="r",
            status="completed",
            incomplete_details=None,
            output_text='{"expression":0}',
            usage=None,
        )

    backend, _ = make_backend(tmp_path, monkeypatch, create)
    result = backend.propose(REFERENCES["best_fit"], 1.0, random.Random(0))
    assert result.status == "missing_usage"


def test_plain_http_endpoint_is_rejected_before_network(tmp_path, monkeypatch):
    backend, _ = make_backend(tmp_path, monkeypatch, lambda **kwargs: None)
    assert backend.kind == "api"
    monkeypatch.setenv("LLM_BASE_URL", "http://example.com/v1")
    with pytest.raises(ValueError, match="HTTPS"):
        APIBackend(tmp_path / ".env", 2048)
