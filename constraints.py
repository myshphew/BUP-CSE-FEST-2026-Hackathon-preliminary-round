"""Compile already-validated directives into immutable hourly LP bounds."""

from dataclasses import dataclass

from models import Directive, Scenario


@dataclass(frozen=True)
class HourBounds:
    solar: float
    reserve: float
    charge: float
    discharge: float
    grid_cap: float | None


def compile_constraints(scenario: Scenario, directives: list[Directive]) -> list[HourBounds]:
    bounds = []
    battery = scenario.battery
    for hour in sorted(scenario.hours, key=lambda x: x.hour):
        solar = hour.solar_kwh
        reserve = battery.minimum_energy_kwh
        charge = battery.max_charge_kwh_per_hour
        discharge = battery.max_discharge_kwh_per_hour
        cap = None
        for d in directives:
            a = d.structured_adjustment
            if a is None or hour.hour not in a.hours:
                continue
            if d.directive_type == "solar_reduction":
                solar *= a.factor
            elif d.directive_type == "minimum_battery_reserve":
                reserve = max(reserve, a.minimum_energy_kwh)
            elif d.directive_type == "max_grid_window":
                cap = a.max_grid_kwh if cap is None else min(cap, a.max_grid_kwh)
            elif d.directive_type == "no_charge_window":
                charge = 0.0
            elif d.directive_type == "no_discharge_window":
                discharge = 0.0
        bounds.append(HourBounds(solar, reserve, charge, discharge, cap))
    return bounds
