import math

import pytest
from pydantic import ValidationError

from errors import InterpretationError
from models import Scenario
from validator import validate_interpretation


@pytest.mark.parametrize("change", [
    lambda d: d.pop("battery"),
    lambda d: d.update(unknown=1),
    lambda d: d.update(operator_notes=[]),
    lambda d: d.update(operator_notes=[" "]),
    lambda d: d.update(operator_notes=["x"] * 4),
    lambda d: d.update(scenario_id=""),
    lambda d: d["hours"].pop(),
    lambda d: d["hours"][0].update(hour=1),
    lambda d: d["hours"][0].update(hour=True),
    lambda d: d["hours"][0].update(hour=0.0),
    lambda d: d["hours"][0].update(demand_kwh=-1),
    lambda d: d["hours"][0].update(demand_kwh="90"),
    lambda d: d["hours"][0].update(demand_kwh=True),
    lambda d: d["hours"][0].update(solar_kwh=math.nan),
    lambda d: d["hours"][0].update(tariff_bdt_per_kwh=math.inf),
    lambda d: d["battery"].update(initial_energy_kwh=1000),
    lambda d: d["battery"].update(initial_energy_kwh=0),
    lambda d: d["battery"].update(max_charge_kwh_per_hour=-1),
])
def test_invalid_requests_rejected(case, change):
    change(case["input"])
    with pytest.raises(ValidationError):
        Scenario.model_validate(case["input"])


@pytest.mark.parametrize("change", [
    lambda ds: ds.pop(),
    lambda ds: ds.reverse(),
    lambda ds: ds[1].update(note_index=0),
    lambda ds: ds[0].update(note_index=True),
    lambda ds: ds[0].update(applies=False),
    lambda ds: ds[0].update(applies=1),
    lambda ds: ds[1].update(applies=True),
    lambda ds: ds[1].update(structured_adjustment={"hours": [0]}),
    lambda ds: ds[0].update(directive_type="change_tariff"),
    lambda ds: ds[0].update(structured_adjustment=None),
    lambda ds: ds[0].update(explanation=""),
    lambda ds: ds[0].update(code="print('never execute')"),
    lambda ds: ds[0]["structured_adjustment"].update(hours=[]),
    lambda ds: ds[0]["structured_adjustment"].update(hours=[13, 12]),
    lambda ds: ds[0]["structured_adjustment"].update(hours=[12, 12]),
    lambda ds: ds[0]["structured_adjustment"].update(hours=[24]),
    lambda ds: ds[0]["structured_adjustment"].update(hours=[False]),
    lambda ds: ds[0]["structured_adjustment"].update(hours=[12.0]),
    lambda ds: ds[0]["structured_adjustment"].update(factor=1.01),
    lambda ds: ds[0]["structured_adjustment"].update(factor=-0.01),
    lambda ds: ds[0]["structured_adjustment"].update(factor="0.2"),
    lambda ds: ds[0]["structured_adjustment"].update(factor=True),
    lambda ds: ds[0]["structured_adjustment"].update(factor=math.nan),
    lambda ds: ds[0]["structured_adjustment"].update(factor=math.inf),
    lambda ds: ds[0]["structured_adjustment"].update(tariff_bdt_per_kwh=0),
    lambda ds: ds[0].update(directive_type="minimum_battery_reserve", structured_adjustment={"hours": [18], "minimum_energy_kwh": 221}),
    lambda ds: ds[0].update(directive_type="minimum_battery_reserve", structured_adjustment={"hours": [18], "minimum_energy_kwh": -1}),
    lambda ds: ds[0].update(directive_type="max_grid_window", structured_adjustment={"hours": [18], "max_grid_kwh": -1}),
])
def test_untrusted_directives_rejected(case, scenario, change):
    ds = case["expected_output"]["directive_interpretation"]
    change(ds)
    with pytest.raises(InterpretationError):
        validate_interpretation({"directive_interpretation": ds}, scenario)


@pytest.mark.parametrize("raw", ["not json", "[]", "null", '{"directive_interpretation":[],"directive_interpretation":[]}', {"hourly_plan": []}])
def test_malformed_model_output(scenario, raw):
    with pytest.raises(InterpretationError):
        validate_interpretation(raw, scenario)


def test_unordered_request_hours_are_supported(case):
    case["input"]["hours"].reverse()
    assert Scenario.model_validate(case["input"]).hours[0].hour == 23
