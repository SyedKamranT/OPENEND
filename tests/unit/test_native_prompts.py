from pathlib import Path

import pytest

from openend.native_prompts import eoh_prompt, funsearch_prompt

ROOT = Path(__file__).resolve().parents[2]


def test_eoh_native_prompts_keep_code_description_and_all_operators():
    parent = {
        "algorithm": "Best Fit",
        "code": "def score(item,bins): return -(bins-item)",
        "objective": 1234567,
    }
    for op in ("i1", "e1", "e2", "m1", "m2", "m3"):
        prompt = eoh_prompt(ROOT, op, [parent, parent])
        assert "scores" in prompt
        if op != "m3":
            assert "Numpy arrays" in prompt
        assert "1234567" not in prompt
        if op != "i1":
            assert parent["code"] in prompt


def test_funsearch_native_prompt_renames_recursion_and_leaves_completion_header():
    implementation = "def priority(item, bins):\n  return priority(item, bins)\n"
    prompt = funsearch_prompt(ROOT, "import numpy as np\n" + implementation, [implementation])
    assert "def priority_v0(" in prompt
    assert "return priority_v0(item, bins)" in prompt
    assert "def priority_v1(" in prompt
    assert "Improved version of `priority_v0`." in prompt
    assert "return priority(item" not in prompt
    with pytest.raises(ValueError):
        funsearch_prompt(ROOT, implementation, [])
