import pytest

from openend.benchmark import Instance, check_certificate, reference_pack
from openend.signal_diagnostic import candidates, decreasing_certificate
from openend.utility_runner import parse


def test_hindsight_certificates_map_back_to_original_order():
    instance = Instance("witness", "test", 10, (2, 5, 4, 7, 1, 3, 8))
    for best in (False, True):
        assignments = decreasing_certificate(instance, best)
        assert check_certificate(instance, assignments) == 3
        assert reference_pack("best_fit", instance)[0] == 4
        assert assignments[0] == 0


def test_diagnostic_search_discloses_proposal_language_extension():
    proposals = list(candidates())
    assert len(proposals) == 84
    for _, t, policy in proposals:
        text = '{"expression":' + policy.expression_json + "}"
        if t in (0, 0.5, 1):
            assert parse(text) == policy
        else:
            with pytest.raises(ValueError, match="finite proposal grammar"):
                parse(text)
