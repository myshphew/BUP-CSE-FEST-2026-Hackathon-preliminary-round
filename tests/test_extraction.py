import json

import pytest

from config import Settings
from errors import InterpretationError
from validator import validate_extraction, validate_interpretation


def compact(case):
    return {"directives": [{k: v for k, v in d.items() if k not in {"applies", "explanation"}}
        for d in case["expected_output"]["directive_interpretation"]]}


def test_compact_extraction_preserves_semantics(case, scenario):
    result = validate_extraction(json.dumps(compact(case)), scenario)
    actual = validate_interpretation(result, scenario)
    expected = case["expected_output"]["directive_interpretation"]
    for left, right in zip(actual, expected):
        assert left.model_dump(exclude={"explanation"}) == {k: v for k, v in right.items() if k != "explanation"}
        assert left.explanation


@pytest.mark.parametrize("mutation", [
    lambda d: d["directives"].pop(),
    lambda d: d["directives"].reverse(),
    lambda d: d["directives"][1].update(note_index=0),
    lambda d: d["directives"][0].update(applies=False),
    lambda d: d["directives"][0].update(explanation="Untrusted extra text"),
    lambda d: d["directives"][0]["structured_adjustment"].update(factor="0.25"),
    lambda d: d["directives"][0].update(directive_type="minimum_battery_reserve", structured_adjustment={"hours": [18], "minimum_energy_kwh": 221}),
    lambda d: d["directives"][1].update(structured_adjustment={"hours": [0]}),
])
def test_compact_guardrails_do_not_repair_bad_model_output(case, scenario, mutation):
    payload = compact(case)
    mutation(payload)
    with pytest.raises(InterpretationError):
        validate_extraction(json.dumps(payload), scenario)


@pytest.mark.parametrize("model", ["gpt-5.6-sol", "gpt-5.6-terra"])
def test_none_reasoning_supported_for_candidate_models(model):
    assert Settings(model=model, reasoning_effort="none").reasoning_effort == "none"


def test_astra_cannot_use_none_reasoning():
    with pytest.raises(ValueError):
        Settings(model="gpt-6-astra", reasoning_effort="none")
