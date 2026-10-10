"""Finite output grammar for local calibration; evaluator remains independent."""

from .policy import FEATURES


def policy_schema():
    # Four operator levels imply at most 31 nodes for a binary expression.
    leaf = {"enum": [*FEATURES, -2, -1, -0.5, 0, 0.5, 1, 2]}
    definitions = {"depth0": leaf}
    for depth in range(1, 5):
        child = {"$ref": f"#/$defs/depth{depth - 1}"}
        choices = [leaf]
        for operators, arity in [
            (["abs", "neg"], 1),
            (["add", "sub", "mul", "div", "min", "max"], 2),
        ]:
            choices.append(
                {
                    "type": "array",
                    "prefixItems": [{"enum": operators}] + [child] * arity,
                    "minItems": arity + 1,
                    "maxItems": arity + 1,
                }
            )
        definitions[f"depth{depth}"] = {"anyOf": choices}
    return {
        "type": "object",
        "properties": {"expression": {"$ref": "#/$defs/depth4"}},
        "required": ["expression"],
        "additionalProperties": False,
        "$defs": definitions,
    }


GRAMMAR_INSTRUCTIONS = """
The response is constrained by a finite JSON schema. Use at most four nested operator levels.
Constants allowed in this experiment: -2, -1, -0.5, 0, 0.5, 1, 2.
Features are JSON strings, operators are JSON arrays, and constants are JSON numbers.
Unary example: {"expression":["neg","gap"]}
Binary syntax example: {"expression":["sub","fraction","index"]}
Nested syntax example: {"expression":["add",["neg","gap"],["mul",0.5,"exact_fit"]]}
Each binary operator takes exactly two arguments; each unary operator takes exactly one.
Return a small variation of the supplied parent. These examples explain syntax, not quality.
"""
