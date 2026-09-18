import pytest

from errors import ScheduleError
from optimizer import optimize
from schedule_validator import validate_schedule


@pytest.mark.parametrize("mutation", [
    lambda r: r.update(scenario_id="wrong"),
    lambda r: r["hourly_plan"].pop(),
    lambda r: r["hourly_plan"].reverse(),
    lambda r: r["hourly_plan"][0].update(hour=1),
    lambda r: r["hourly_plan"][0].update(grid_kwh=-1),
    lambda r: r["hourly_plan"][0].update(grid_kwh=999),
    lambda r: r["hourly_plan"][0].update(grid_kwh=float("nan")),
    lambda r: r["hourly_plan"][0].update(solar_used_kwh=1),
    lambda r: r["hourly_plan"][12].update(solar_used_kwh=100),
    lambda r: r["hourly_plan"][0].update(battery_kwh=500),
    lambda r: r["hourly_plan"][0].update(battery_action="idle", battery_kwh=1),
    lambda r: r["hourly_plan"][0].update(battery_energy_after_kwh=999),
    lambda r: r["hourly_plan"][-1].update(battery_energy_after_kwh=100),
    lambda r: r.update(total_grid_kwh=r["total_grid_kwh"] + 0.02),
    lambda r: r.update(total_cost_bdt=r["total_cost_bdt"] + 0.02),
    lambda r: r.update(peak_grid_kwh=r["peak_grid_kwh"] + 0.02),
])
def test_corrupted_schedules_rejected(case, scenario, mutation):
    response = case["expected_output"]
    mutation(response)
    with pytest.raises(ScheduleError):
        validate_schedule(scenario, response)


def test_numeric_tolerance_is_absolute(case, scenario):
    response = case["expected_output"]
    response["total_cost_bdt"] += 0.009
    validate_schedule(scenario, response)
    response["total_cost_bdt"] += 0.002
    with pytest.raises(ScheduleError):
        validate_schedule(scenario, response)


def test_replay_recomputes_constraints_independently(scenario, directives, monkeypatch):
    import optimizer
    from dataclasses import replace
    actual = optimizer.compile_constraints
    def wrong(s, ds):
        return [replace(b, solar=s.hours[h].solar_kwh) for h, b in enumerate(actual(s, ds))]
    monkeypatch.setattr(optimizer, "compile_constraints", wrong)
    result = optimize(scenario, directives)
    with pytest.raises(ScheduleError):
        validate_schedule(scenario, result)
