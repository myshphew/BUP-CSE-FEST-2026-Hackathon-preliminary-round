"""Unit variants derived in memory from official inputs, never replacement samples."""

import copy
import random

import pytest

from constraints import compile_constraints
from errors import InfeasibleError, SolverError
from models import Scenario
from optimizer import optimize
from schedule_validator import validate_schedule
from validator import validate_interpretation


def with_directives(case, descriptions):
    data = copy.deepcopy(case["input"])
    # Labels are test-only; interpretation is explicitly supplied to unit-test math.
    data["operator_notes"] = ["Unit constraint variant"] * len(descriptions)
    scenario = Scenario.model_validate(data)
    raw = [{"note_index": i, "applies": kind != "no_op", "directive_type": kind,
            "structured_adjustment": adjustment, "explanation": "Unit constraint variant"}
           for i, (kind, adjustment) in enumerate(descriptions)]
    return scenario, validate_interpretation({"directive_interpretation": raw}, scenario)


@pytest.mark.parametrize("kind, values, field, expected", [
    ("solar_reduction", [{"factor": 0.5}, {"factor": 0.2}], "solar", 18.0),
    ("minimum_battery_reserve", [{"minimum_energy_kwh": 80}, {"minimum_energy_kwh": 120}], "reserve", 120),
    ("max_grid_window", [{"max_grid_kwh": 120}, {"max_grid_kwh": 100}], "grid_cap", 100),
    ("no_charge_window", [{}, {}], "charge", 0),
    ("no_discharge_window", [{}, {}], "discharge", 0),
])
def test_overlapping_directives(case, kind, values, field, expected):
    descriptions = [(kind, {"hours": [12], **value}) for value in values]
    scenario, directives = with_directives(case, descriptions)
    bounds = compile_constraints(scenario, directives)
    assert getattr(bounds[12], field) == pytest.approx(expected)
    validate_schedule(scenario, optimize(scenario, directives))


def test_charge_and_discharge_blocked_means_idle(case):
    scenario, directives = with_directives(case, [
        ("no_charge_window", {"hours": list(range(24))}),
        ("no_discharge_window", {"hours": list(range(24))}),
    ])
    result = validate_schedule(scenario, optimize(scenario, directives))
    assert all(h.battery_action == "idle" for h in result.hourly_plan)


def test_infeasible_grid_cap_fails(case):
    scenario, directives = with_directives(case, [
        ("max_grid_window", {"hours": [0], "max_grid_kwh": 0}),
        ("no_discharge_window", {"hours": [0]}),
    ])
    with pytest.raises(InfeasibleError):
        optimize(scenario, directives)


def test_end_of_day_reserve_cannot_override_neutrality(case):
    scenario, directives = with_directives(case, [
        ("minimum_battery_reserve", {"hours": [23], "minimum_energy_kwh": 200}),
    ])
    with pytest.raises(InfeasibleError):
        optimize(scenario, directives)


@pytest.mark.parametrize("variant", ["zero_battery", "zero_rates", "zero_tariffs", "zero_demand", "surplus_solar", "fractional"])
def test_numeric_edges(case, variant):
    data = case["input"]
    if variant == "zero_battery":
        data["battery"] = {key: 0 for key in data["battery"]}
    if variant == "zero_rates":
        data["battery"]["max_charge_kwh_per_hour"] = 0
        data["battery"]["max_discharge_kwh_per_hour"] = 0
    for h in data["hours"]:
        if variant == "zero_tariffs": h["tariff_bdt_per_kwh"] = 0
        if variant == "zero_demand": h["demand_kwh"] = 0
        if variant == "surplus_solar": h["solar_kwh"] = 1000
        if variant == "fractional":
            h["demand_kwh"] /= 7
            h["solar_kwh"] /= 11
            h["tariff_bdt_per_kwh"] /= 3
    scenario, directives = with_directives(case, [("no_op", None)])
    result = validate_schedule(scenario, optimize(scenario, directives))
    if variant in {"zero_tariffs", "zero_demand", "surplus_solar"}:
        assert result.total_cost_bdt == pytest.approx(0)


@pytest.mark.parametrize("seed", range(12))
def test_optimal_cost_against_independent_integer_dynamic_program(case, seed):
    # Integer data gives an integral optimum for this network-flow LP. Exhaustive
    # state enumeration is an independent small-instance optimality oracle.
    rng = random.Random(seed)
    data = case["input"]
    data["battery"] = dict(capacity_kwh=4, initial_energy_kwh=2, minimum_energy_kwh=0,
                           max_charge_kwh_per_hour=2, max_discharge_kwh_per_hour=2)
    for h in data["hours"]:
        h.update(demand_kwh=rng.randrange(4), solar_kwh=rng.randrange(5), tariff_bdt_per_kwh=rng.randrange(8))
    scenario, directives = with_directives(case, [("no_op", None)])
    states = {2: 0}
    for hour in data["hours"]:
        next_states = {}
        for before, cost in states.items():
            for after in range(5):
                change = after - before
                if abs(change) > 2 or hour["demand_kwh"] + change < 0:
                    continue
                grid = max(0, hour["demand_kwh"] + change - hour["solar_kwh"])
                candidate = cost + grid * hour["tariff_bdt_per_kwh"]
                next_states[after] = min(next_states.get(after, float("inf")), candidate)
        states = next_states
    result = validate_schedule(scenario, optimize(scenario, directives))
    assert result.total_cost_bdt == pytest.approx(states[2], abs=0.01)


def test_solver_failure_is_controlled(scenario, directives, monkeypatch):
    import pulp
    def broken(*args, **kwargs):
        raise pulp.PulpSolverError("private internal details")
    monkeypatch.setattr(pulp.LpProblem, "solve", broken)
    with pytest.raises(SolverError):
        optimize(scenario, directives)
