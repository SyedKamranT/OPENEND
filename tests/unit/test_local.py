import random
from urllib.error import URLError

import pytest

from openend.local import LocalBackend
from openend.policy import REFERENCES


def setup_backend(monkeypatch, reply=None, remote=False, structured=False):
    calls = []
    record = {"name": "test:1b", "digest": "fixed", "details": {"family": "test"}}
    if remote:
        record["remote_host"] = "https://example.com"

    def request(self, route, payload=None):
        calls.append((route, payload))
        if route == "version":
            return {"version": "test"}
        if route == "tags":
            return {"models": [record]}
        if route == "show":
            return {}
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(LocalBackend, "_request", request)
    return LocalBackend("test:1b", 512, structured=structured), calls, record


def response(**updates):
    return {
        "model": "test:1b",
        "done": True,
        "done_reason": "stop",
        "message": {"content": '{"expression":0}'},
        "prompt_eval_count": 100,
        "eval_count": 10,
        **updates,
    }


def test_local_budget_seed_and_model_identity(monkeypatch):
    backend, calls, _ = setup_backend(monkeypatch, response())
    result = backend.propose(REFERENCES["first_fit"], 0.9, random.Random(42))
    assert result.status == "ok"
    assert result.usage["total_tokens"] == 110
    assert result.metadata["model"] == "test:1b@fixed"
    request = calls[-1][1]
    assert request["think"] is False
    assert request["options"]["num_ctx"] == 8192
    assert request["options"]["num_predict"] == 512
    assert request["options"]["seed"] == random.Random(42).randrange(2**31)
    assert "test/" not in str(request)


@pytest.mark.parametrize(
    "reply,status",
    [
        (response(eval_count=None), "missing_usage"),
        (response(done_reason="length"), "incomplete_response"),
        (response(model="different"), "model_changed"),
    ],
)
def test_local_incomplete_responses_are_not_success(monkeypatch, reply, status):
    backend, _, _ = setup_backend(monkeypatch, reply)
    assert backend.propose(REFERENCES["first_fit"], 1, random.Random()).status == status


def test_local_rejects_remote_and_changed_weights(monkeypatch):
    with pytest.raises(ValueError, match="cloud"):
        setup_backend(monkeypatch, remote=True)
    backend, calls, _ = setup_backend(monkeypatch, response())
    monkeypatch.setattr(backend, "_model_record", lambda: {"digest": "changed"})
    assert backend.propose(REFERENCES["first_fit"], 1, random.Random()).status == "model_changed"
    assert not any(route == "chat" for route, _ in calls)


def test_local_no_retry_after_transport_failure(monkeypatch):
    backend, calls, _ = setup_backend(monkeypatch, URLError("unavailable"))
    for _ in range(2):
        assert backend.propose(REFERENCES["first_fit"], 1, random.Random()).status == "api_error"
    assert sum(route == "chat" for route, _ in calls) == 1


def test_structured_schema_and_prompt_are_sent_and_recorded(monkeypatch):
    backend, calls, _ = setup_backend(monkeypatch, response(), structured=True)
    backend.propose(REFERENCES["first_fit"], 1, random.Random(42))
    request = calls[-1][1]
    identity = backend.identity()
    assert request["format"] == identity["format"]
    assert request["format"]["additionalProperties"] is False
    assert request["messages"][0]["content"] == identity["system_prompt"]
    assert "exactly two arguments" in identity["system_prompt"]


def test_schema_largest_binary_tree_stays_inside_independent_policy_limits():
    from openend.grammar import policy_schema
    from openend.policy import Policy

    schema = policy_schema()
    node = "gap"
    for depth in range(1, 5):
        branch = schema["$defs"][f"depth{depth}"]["anyOf"][2]
        assert branch["minItems"] == branch["maxItems"] == 3
        assert branch["prefixItems"][1] == {"$ref": f"#/$defs/depth{depth - 1}"}
        node = ["add", node, node]
    Policy.from_object({"expression": node})
