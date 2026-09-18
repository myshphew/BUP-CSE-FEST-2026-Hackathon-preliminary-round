import copy
import json
from pathlib import Path

import pytest

from models import Scenario
from validator import validate_interpretation

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "BUP_CSE_FEST_2026_Preli_Public_Sample_Cases.json"
CASES = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))["cases"]


@pytest.fixture
def case():
    return copy.deepcopy(CASES[0])


@pytest.fixture
def scenario(case):
    return Scenario.model_validate(case["input"])


@pytest.fixture
def directives(case, scenario):
    return validate_interpretation({"directive_interpretation": case["expected_output"]["directive_interpretation"]}, scenario)
