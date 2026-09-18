"""Independent audit oracles; unit variants never replace organizer cases."""

import random

import pulp
import pytest

from conftest import CASES
from errors import InfeasibleError
from models import Scenario
from optimizer import optimize
from schedule_validator import validate_schedule
from test_optimizer import with_directives
from validator import validate_interpretation


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_peak_refinement_preserves_official_optimum(case):
    scenario = Scenario.model_validate(case["input"])
    directives = validate_interpretation({"directive_interpretation": case["expected_output"]["directive_interpretation"]}, scenario)
    primary = validate_schedule(scenario, optimize(scenario, directives, minimize_peak=False))
    refined = validate_schedule(scenario, optimize(scenario, directives))
    assert refined.total_cost_bdt == pytest.approx(case["expected_output"]["total_cost_bdt"], abs=0.001)
    assert refined.peak_grid_kwh <= primary.peak_grid_kwh + 1e-7
    if case["id"] == "SAMPLE-01":
        assert refined.peak_grid_kwh == pytest.approx(175)
    if case["id"] == "SAMPLE-09":
        assert refined.peak_grid_kwh == pytest.approx(170)


@pytest.mark.parametrize("first_tariff,expected_peak", [(1, 5), (10, 10)])
def test_peak_minimization_never_buys_more_expensive_energy(case, first_tariff, expected_peak):
    # One 10 kWh load in hour 1. At equal prices, shifting half to hour 0
    # gives the provable 5 kWh minimum peak. If hour 0 is dearer, do not shift.
    data = case["input"]
    data["battery"] = dict(capacity_kwh=10, initial_energy_kwh=0, minimum_energy_kwh=0,
                           max_charge_kwh_per_hour=10, max_discharge_kwh_per_hour=10)
    for hour in data["hours"]:
        hour.update(demand_kwh=10 if hour["hour"] == 1 else 0, solar_kwh=0,
                    tariff_bdt_per_kwh=first_tariff if hour["hour"] == 0 else 1)
    scenario, directives = with_directives(case, [("no_op", None)])
    result = validate_schedule(scenario, optimize(scenario, directives))
    assert result.total_cost_bdt == pytest.approx(10, abs=1e-7)
    assert result.peak_grid_kwh == pytest.approx(expected_peak, abs=1e-7)


@pytest.mark.parametrize("failure", ["timeout", "exception", "wrong_cost"])
def test_secondary_failure_preserves_primary_optimal_plan(scenario, directives, monkeypatch, failure):
    primary = optimize(scenario, directives, minimize_peak=False)
    solve = pulp.LpProblem.solve
    calls = 0

    def unreliable_secondary(problem, *args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return solve(problem, *args, **kwargs)
        if failure == "exception":
            raise pulp.PulpSolverError("Secondary solve failed")
        if failure == "timeout":
            problem.status = pulp.LpStatusNotSolved
            for variable in problem.variables():
                variable.varValue = 999
        else:
            solve(problem, *args, **kwargs)
            next(v for v in problem.variables() if v.name == "grid_00").varValue += 1
        return problem.status

    monkeypatch.setattr(pulp.LpProblem, "solve", unreliable_secondary)
    result = validate_schedule(scenario, optimize(scenario, directives))
    assert result.model_dump() == primary.model_dump()


@pytest.mark.parametrize("seed", range(48))
def test_fractional_directive_combinations_against_independent_dp(case, seed):
    # Enumerate all battery states in quarter-kWh units. The constraint matrix
    # is a flow network, so integral scaled bounds admit an integral optimum.
    # This oracle independently applies the directives, without the LP compiler.
    rng = random.Random(seed)
    unit = 0.25
    data = case["input"]
    data["battery"] = dict(capacity_kwh=4 * unit, initial_energy_kwh=2 * unit,
                           minimum_energy_kwh=0, max_charge_kwh_per_hour=2 * unit,
                           max_discharge_kwh_per_hour=2 * unit)
    for hour in data["hours"]:
        hour.update(demand_kwh=rng.randrange(5) * unit, solar_kwh=rng.randrange(3) * 4 * unit,
                    tariff_bdt_per_kwh=rng.randrange(9) / 7)
    window = sorted(rng.sample(range(24), 6))
    patterns = [
        [("solar_reduction", {"hours": window, "factor": 0.5}),
         ("solar_reduction", {"hours": window, "factor": 0.5})],
        [("minimum_battery_reserve", {"hours": window, "minimum_energy_kwh": unit}),
         ("minimum_battery_reserve", {"hours": window, "minimum_energy_kwh": 3 * unit})],
        [("max_grid_window", {"hours": window, "max_grid_kwh": 2 * unit}),
         ("max_grid_window", {"hours": window, "max_grid_kwh": unit})],
        [("no_charge_window", {"hours": window}),
         ("no_discharge_window", {"hours": window})],
        [("no_charge_window", {"hours": window}),
         ("minimum_battery_reserve", {"hours": [10, 11], "minimum_energy_kwh": 2 * unit}),
         ("max_grid_window", {"hours": [7, 8, 9], "max_grid_kwh": 2 * unit})],
        [("solar_reduction", {"hours": window, "factor": 0.25}),
         ("no_discharge_window", {"hours": [10, 11, 12]}),
         ("minimum_battery_reserve", {"hours": [20, 21], "minimum_energy_kwh": 3 * unit})],
    ]
    descriptions = patterns[seed % len(patterns)]
    scenario, directives = with_directives(case, descriptions)
    states = {2: 0.0}
    for hour in data["hours"]:
        solar, reserve, cap = hour["solar_kwh"], 0, float("inf")
        charge_limit = discharge_limit = 2
        for kind, adjustment in descriptions:
            if hour["hour"] not in adjustment["hours"]:
                continue
            if kind == "solar_reduction": solar *= adjustment["factor"]
            if kind == "minimum_battery_reserve": reserve = max(reserve, adjustment["minimum_energy_kwh"])
            if kind == "max_grid_window": cap = min(cap, adjustment["max_grid_kwh"])
            if kind == "no_charge_window": charge_limit = 0
            if kind == "no_discharge_window": discharge_limit = 0
        next_states = {}
        for before, cost in states.items():
            for after in range(5):
                change = after - before
                if not -discharge_limit <= change <= charge_limit or after * unit < reserve:
                    continue
                required = hour["demand_kwh"] + change * unit
                if required < 0:
                    continue
                grid = max(0, required - solar)
                if grid > cap:
                    continue
                candidate = cost + grid * hour["tariff_bdt_per_kwh"]
                next_states[after] = min(next_states.get(after, float("inf")), candidate)
        states = next_states
    if 2 not in states:
        with pytest.raises(InfeasibleError):
            optimize(scenario, directives)
    else:
        result = validate_schedule(scenario, optimize(scenario, directives), ground_truth=directives)
        assert result.total_cost_bdt == pytest.approx(states[2], abs=0.0001)
