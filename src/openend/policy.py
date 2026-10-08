"""A bounded expression language: model responses are data, never Python code."""

import json
import math
import random
from dataclasses import dataclass

from .artifacts import canonical, digest

FEATURES = ("gap", "remaining", "item", "index", "fraction", "exact_fit")
ARITY = {"add": 2, "sub": 2, "mul": 2, "div": 2, "min": 2, "max": 2, "abs": 1, "neg": 1}
MAX_NODES = 31
MAX_DEPTH = 6
MAX_RESPONSE_BYTES = 16384


class InvalidPolicy(ValueError):
    pass


def _validate(node, depth=0):
    if depth > MAX_DEPTH:
        raise InvalidPolicy("expression depth exceeded")
    if type(node) in (int, float):
        if not math.isfinite(node) or abs(node) > 10:
            raise InvalidPolicy("constant must be finite and within [-10, 10]")
        return 1
    if isinstance(node, str) and node in FEATURES:
        return 1
    if not isinstance(node, list) or not node or not isinstance(node[0], str):
        raise InvalidPolicy("expected a number, feature, or operator array")
    if node[0] not in ARITY or len(node) != ARITY[node[0]] + 1:
        raise InvalidPolicy("unknown operator or wrong arity")
    count = 1 + sum(_validate(child, depth + 1) for child in node[1:])
    if count > MAX_NODES:
        raise InvalidPolicy("expression node limit exceeded")
    return count


def _score(node, values):
    if type(node) in (int, float):
        return float(node)
    if isinstance(node, str):
        return values[node]
    op = node[0]
    a = _score(node[1], values)
    if op == "abs":
        result = abs(a)
    elif op == "neg":
        result = -a
    else:
        b = _score(node[2], values)
        if op == "add":
            result = a + b
        elif op == "sub":
            result = a - b
        elif op == "mul":
            result = a * b
        elif op == "div":
            result = a / b if abs(b) >= 1e-6 else 0.0
        elif op == "min":
            result = min(a, b)
        else:
            result = max(a, b)
    return max(-1e6, min(1e6, result))


@dataclass(frozen=True)
class Policy:
    # Store canonical JSON rather than mutable trees; validate before construction.
    expression_json: str

    def __post_init__(self):
        if len(self.expression_json.encode("utf-8")) > MAX_RESPONSE_BYTES:
            raise InvalidPolicy("expression too large")
        try:
            _validate(json.loads(self.expression_json))
        except (json.JSONDecodeError, RecursionError) as exc:
            raise InvalidPolicy("invalid expression") from exc

    @classmethod
    def from_object(cls, value):
        if not isinstance(value, dict) or set(value) != {"expression"}:
            raise InvalidPolicy("exactly one field, expression, is required")
        try:
            _validate(value["expression"])
            return cls(canonical(value["expression"]))
        except (RecursionError, OverflowError, ValueError) as exc:
            raise InvalidPolicy("invalid or oversized expression") from exc

    @classmethod
    def from_text(cls, text):
        if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_RESPONSE_BYTES:
            raise InvalidPolicy("response too large or not text")

        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise InvalidPolicy("duplicate JSON keys")
                result[key] = value
            return result

        try:
            return cls.from_object(json.loads(text, object_pairs_hook=unique_keys))
        except (json.JSONDecodeError, RecursionError) as exc:
            raise InvalidPolicy("response must be a JSON object without code fences") from exc

    def to_object(self):
        return {"expression": json.loads(self.expression_json)}

    @property
    def identity(self):
        return digest(self.to_object())

    def choose(self, item, remaining, capacity):
        feasible = [i for i, space in enumerate(remaining) if space >= item]
        if not feasible:
            return len(remaining)
        expression = json.loads(self.expression_json)

        def score(i):
            space = remaining[i]
            return _score(
                expression,
                {
                    "gap": (space - item) / capacity,
                    "remaining": space / capacity,
                    "item": item / capacity,
                    "index": i / max(1, len(remaining) - 1),
                    "fraction": item / space,
                    "exact_fit": float(space == item),
                },
            )

        # Stable earliest-bin tie break in every condition.
        return max(feasible, key=lambda i: (score(i), -i))


REFERENCES = {
    "first_fit": Policy.from_object({"expression": 0}),
    "best_fit": Policy.from_object({"expression": ["neg", "gap"]}),
    "worst_fit": Policy.from_object({"expression": "gap"}),
}


def mutate(parent, rng: random.Random):
    """One shared mutation operator; condition never enters this function."""
    tree = parent.to_object()["expression"]
    paths = []

    def walk(node, path):
        paths.append(path)
        if isinstance(node, list):
            for i in range(1, len(node)):
                walk(node[i], path + [i])

    walk(tree, [])
    path = rng.choice(paths)
    leaf = rng.choice(list(FEATURES) + [-2, -1, -0.5, 0, 0.5, 1, 2])
    replacement = (
        leaf
        if rng.random() < 0.4
        else [
            rng.choice(["add", "sub", "mul", "div", "min", "max"]),
            leaf,
            rng.choice(list(FEATURES) + [-1, 0.5, 1]),
        ]
    )
    if not path:
        tree = replacement
    else:
        target = tree
        for index in path[:-1]:
            target = target[index]
        target[path[-1]] = replacement
    # Invalid mutations remain generated attempts; no free repair/resampling.
    return canonical({"expression": tree})
