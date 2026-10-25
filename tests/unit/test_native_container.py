import pytest

from openend.native_container import command


def test_container_contract_requires_immutable_image_and_no_host_mounts():
    with pytest.raises(ValueError, match="image ID"):
        command("docker", "python:latest", "test")
    args = command("docker", "sha256:" + "a" * 64, "test")
    for flag, value in [
        ("--network", "none"),
        ("--cap-drop", "ALL"),
        ("--user", "65534:65534"),
        ("--memory", "256m"),
        ("--pids-limit", "32"),
        ("--security-opt", "no-new-privileges"),
    ]:
        assert args[args.index(flag) + 1] == value
    assert "--read-only" in args
    assert not any(x in args for x in ("--mount", "-v", "--privileged", "--env-file"))


def test_containment_probe_sources_parse_without_host_execution():
    import ast

    from openend.native_containment_audit import cases
    probes = cases()
    assert len({row[0] for row in probes}) == 7
    for _, code, _, _ in probes:
        ast.parse(code)
