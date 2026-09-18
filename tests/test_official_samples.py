import hashlib

import pytest

from models import Scenario
from optimizer import optimize
from schedule_validator import validate_schedule
from validator import validate_interpretation
from conftest import CASES, SAMPLE_PATH


def test_official_file_unchanged():
    assert hashlib.sha256(SAMPLE_PATH.read_bytes()).hexdigest() == "fa6abd71868e0faf429a87429d7d4a2b7bfd38c5551565637498d7fec68d5f32"


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_official_optimal_cost_and_independent_replay(case):
    scenario = Scenario.model_validate(case["input"])
    reference = case["expected_output"]
    directives = validate_interpretation({"directive_interpretation": reference["directive_interpretation"]}, scenario)
    validate_schedule(scenario, reference)
    result = validate_schedule(scenario, optimize(scenario, directives), ground_truth=directives)
    assert abs(result.total_cost_bdt - reference["total_cost_bdt"]) <= 0.01


def test_deterministic_repeated_solves(scenario, directives):
    first = optimize(scenario, directives).model_dump()
    for _ in range(3):
        assert optimize(scenario, directives).model_dump() == first
