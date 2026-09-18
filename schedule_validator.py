"""Independent replay: deliberately does not reuse optimizer/constraint compilation."""

import math

from pydantic import ValidationError

from errors import InterpretationError, ScheduleError
from models import Directive, OptimizationResponse, Scenario
from validator import validate_interpretation

TOLERANCE = 0.01


def validate_schedule(
    scenario: Scenario,
    response: OptimizationResponse | dict,
    ground_truth: list[Directive] | None = None,
) -> OptimizationResponse:
    """Optionally replay under organizer ground truth for the public test runner."""
    def require(condition):
        if not condition:
            raise ScheduleError()

    def close(a, b):
        return abs(a - b) <= TOLERANCE

    try:
        raw = response.model_dump() if isinstance(response, OptimizationResponse) else response
        result = OptimizationResponse.model_validate(raw)
        own = validate_interpretation({"directive_interpretation": [d.model_dump() for d in result.directive_interpretation]}, scenario)
        directives = own if ground_truth is None else validate_interpretation(
            {"directive_interpretation": [d.model_dump() for d in ground_truth]}, scenario,
        )
        require(result.scenario_id == scenario.scenario_id)
        require([p.hour for p in result.hourly_plan] == list(range(24)))
        hours = {h.hour: h for h in scenario.hours}
        battery = scenario.battery
        state = battery.initial_energy_kwh
        for p in result.hourly_plan:
            h = hours[p.hour]
            available_solar = h.solar_kwh
            reserve = battery.minimum_energy_kwh
            charge = p.battery_kwh if p.battery_action == "charge" else 0.0
            discharge = p.battery_kwh if p.battery_action == "discharge" else 0.0
            if p.battery_action == "idle":
                require(p.battery_kwh == 0)
            require(charge <= battery.max_charge_kwh_per_hour + TOLERANCE)
            require(discharge <= battery.max_discharge_kwh_per_hour + TOLERANCE)
            for d in directives:
                a = d.structured_adjustment
                if a is None or p.hour not in a.hours:
                    continue
                if d.directive_type == "solar_reduction":
                    available_solar *= a.factor
                elif d.directive_type == "minimum_battery_reserve":
                    reserve = max(reserve, a.minimum_energy_kwh)
                elif d.directive_type == "max_grid_window":
                    require(p.grid_kwh <= a.max_grid_kwh + TOLERANCE)
                elif d.directive_type == "no_charge_window":
                    require(charge <= TOLERANCE)
                elif d.directive_type == "no_discharge_window":
                    require(discharge <= TOLERANCE)
            require(p.solar_used_kwh <= available_solar + TOLERANCE)
            require(close(p.grid_kwh + p.solar_used_kwh + discharge, h.demand_kwh + charge))
            state = math.fsum([state, charge, -discharge])
            require(close(p.battery_energy_after_kwh, state))
            require(reserve - TOLERANCE <= state <= battery.capacity_kwh + TOLERANCE)
            require(reserve - TOLERANCE <= p.battery_energy_after_kwh <= battery.capacity_kwh + TOLERANCE)
        require(close(state, battery.initial_energy_kwh))
        require(close(result.hourly_plan[-1].battery_energy_after_kwh, battery.initial_energy_kwh))
        require(close(result.total_grid_kwh, math.fsum(p.grid_kwh for p in result.hourly_plan)))
        require(close(result.total_cost_bdt, math.fsum(p.grid_kwh * hours[p.hour].tariff_bdt_per_kwh for p in result.hourly_plan)))
        require(close(result.peak_grid_kwh, max(p.grid_kwh for p in result.hourly_plan)))
        return result
    except (ValidationError, InterpretationError, ValueError, TypeError, OverflowError) as exc:
        raise ScheduleError() from exc
