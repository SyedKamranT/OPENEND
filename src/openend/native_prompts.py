"""Pinned native prompt construction; candidate text is parsed, never executed."""

import __future__

import ast
import copy
import dataclasses
import io
import logging
import sys
import tokenize
from pathlib import Path
from types import ModuleType, SimpleNamespace

from .artifacts import file_hash

PINS = {
    "eoh/eoh__src__eoh__methods__eoh__eoh_evolution.py.txt": "52cef4303c62043e0484f82e77a4ced27eebdea0b6d52572e60f03ae125db455",
    "eoh/eoh__src__eoh__problems__optimization__bp_online__prompts.py.txt": "cfdc833c9c38b1d26e6cb640ae984951bf97a9b03f05a412a9b641cadf71ba62",
    "funsearch/implementation__code_manipulation.py.txt": "8538521e64b0f92a95ee88d0617dd499129a1de19d9502aacba3f109b77f7b3b",
    "funsearch/implementation__programs_database.py.txt": "b2bef312d04861f467f304f65788efe959f0493818976b052c46b4703151affc",
}


def source(root, suffix):
    name = next(n for n in PINS if n.endswith(suffix))
    path = Path(root) / "data/baselines/upstream-v1" / name
    if file_hash(path) != PINS[name]:
        raise ValueError("native prompt source changed")
    return ast.parse(path.read_text())


def compile_nodes(nodes, scope):
    exec(  # noqa: S102 - reviewed fixed-source prompt functions only
        compile(
            ast.Module(body=nodes, type_ignores=[]),
            "<pinned-native-prompt>",
            "exec",
            flags=__future__.annotations.compiler_flag,
        ),
        scope,
    )


def eoh_prompt(root, operator, parents=()):
    scope = {}
    prompt_class = next(
        n for n in source(root, "prompts.py.txt").body if isinstance(n, ast.ClassDef)
    )
    compile_nodes([prompt_class], scope)
    prompts = scope["GetPrompts"]()
    host = SimpleNamespace(**vars(prompts))
    host.joined_inputs = ", ".join("'" + x + "'" for x in host.prompt_func_inputs)
    host.joined_outputs = ", ".join("'" + x + "'" for x in host.prompt_func_outputs)
    if operator not in ("i1", "e1", "e2", "m1", "m2", "m3"):
        raise ValueError("unknown EoH operator")
    cls = next(n for n in source(root, "eoh_evolution.py.txt").body if isinstance(n, ast.ClassDef))
    name = "get_prompt_" + operator
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    compile_nodes([method], scope)
    if operator == "i1":
        return scope[name](host)
    return scope[name](host, list(parents) if operator.startswith("e") else parents[0])


def funsearch_prompt(root, template, implementations, function_name="priority"):
    if not implementations or sum(map(len, implementations)) + len(template) > 65536:
        raise ValueError("bounded nonempty implementations required")
    # Pinned dataclasses need a registered module for postponed type annotations.
    module = ModuleType("_openend_pinned_code_manipulation")
    module.__dict__.update(
        ast=ast, dataclasses=dataclasses, io=io, tokenize=tokenize, logging=logging
    )
    sys.modules[module.__name__] = module
    nodes = [
        n
        for n in source(root, "code_manipulation.py.txt").body
        if isinstance(n, (ast.ClassDef, ast.FunctionDef))
    ]
    compile_nodes(nodes, module.__dict__)
    cls = next(
        n
        for n in source(root, "programs_database.py.txt").body
        if isinstance(n, ast.ClassDef) and n.name == "Island"
    )
    method = next(
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_generate_prompt"
    )
    scope = {"copy": copy, "dataclasses": dataclasses, "code_manipulation": module}
    compile_nodes([method], scope)
    host = SimpleNamespace(
        _function_to_evolve=function_name, _template=module.text_to_program(template)
    )
    return scope["_generate_prompt"](host, [module.text_to_function(x) for x in implementations])
