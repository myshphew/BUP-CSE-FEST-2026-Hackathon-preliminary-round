"""Exact challenge schemas. No numeric/string/bool coercion or extra fields."""

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonNegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
HourIndex = Annotated[int, Field(ge=0, le=23)]
NonEmpty = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Hour(StrictModel):
    hour: HourIndex
    demand_kwh: NonNegative
    solar_kwh: NonNegative
    tariff_bdt_per_kwh: NonNegative


class Battery(StrictModel):
    capacity_kwh: NonNegative
    initial_energy_kwh: NonNegative
    minimum_energy_kwh: NonNegative
    max_charge_kwh_per_hour: NonNegative
    max_discharge_kwh_per_hour: NonNegative

    @model_validator(mode="after")
    def valid_bounds(self):
        if not self.minimum_energy_kwh <= self.initial_energy_kwh <= self.capacity_kwh:
            raise ValueError("Require minimum <= initial <= capacity")
        return self


class Scenario(StrictModel):
    scenario_id: NonEmpty
    operator_notes: Annotated[list[NonEmpty], Field(min_length=1, max_length=3)]
    hours: Annotated[list[Hour], Field(min_length=24, max_length=24)]
    battery: Battery

    @model_validator(mode="after")
    def complete_hours(self):
        if sorted(h.hour for h in self.hours) != list(range(24)):
            raise ValueError("Require exactly one entry per hour 0..23")
        return self


class Window(StrictModel):
    hours: Annotated[list[HourIndex], Field(min_length=1, max_length=24)]

    @model_validator(mode="after")
    def ordered_unique_hours(self):
        if self.hours != sorted(set(self.hours)):
            raise ValueError("Directive hours must be sorted and unique")
        return self


class SolarAdjustment(Window):
    factor: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class ReserveAdjustment(Window):
    minimum_energy_kwh: NonNegative


class GridAdjustment(Window):
    max_grid_kwh: NonNegative


class DirectiveBase(StrictModel):
    note_index: Annotated[int, Field(ge=0, le=2)]
    applies: bool
    explanation: NonEmpty

    @model_validator(mode="after")
    def valid_applies(self):
        if self.applies != (self.directive_type != "no_op"):
            raise ValueError("applies must be false only for no_op")
        return self


class SolarDirective(DirectiveBase):
    directive_type: Literal["solar_reduction"]
    structured_adjustment: SolarAdjustment


class ReserveDirective(DirectiveBase):
    directive_type: Literal["minimum_battery_reserve"]
    structured_adjustment: ReserveAdjustment


class NoChargeDirective(DirectiveBase):
    directive_type: Literal["no_charge_window"]
    structured_adjustment: Window


class NoDischargeDirective(DirectiveBase):
    directive_type: Literal["no_discharge_window"]
    structured_adjustment: Window


class GridDirective(DirectiveBase):
    directive_type: Literal["max_grid_window"]
    structured_adjustment: GridAdjustment


class NoOpDirective(DirectiveBase):
    directive_type: Literal["no_op"]
    structured_adjustment: None


# A nested anyOf is supported by OpenAI Structured Outputs. Each member has an
# exact adjustment shape, avoiding a permissive dictionary with optional keys.
Directive = Union[
    SolarDirective, ReserveDirective, NoChargeDirective,
    NoDischargeDirective, GridDirective, NoOpDirective,
]


class Interpretation(StrictModel):
    directive_interpretation: Annotated[list[Directive], Field(min_length=1, max_length=3)]


# The provider emits only semantic information. Redundant applies/explanation
# fields are generated from these validated directives by deterministic code.
class ExtractedBase(StrictModel):
    note_index: Annotated[int, Field(ge=0, le=2)]


class ExtractedSolar(ExtractedBase):
    directive_type: Literal["solar_reduction"]
    structured_adjustment: SolarAdjustment


class ExtractedReserve(ExtractedBase):
    directive_type: Literal["minimum_battery_reserve"]
    structured_adjustment: ReserveAdjustment


class ExtractedNoCharge(ExtractedBase):
    directive_type: Literal["no_charge_window"]
    structured_adjustment: Window


class ExtractedNoDischarge(ExtractedBase):
    directive_type: Literal["no_discharge_window"]
    structured_adjustment: Window


class ExtractedGrid(ExtractedBase):
    directive_type: Literal["max_grid_window"]
    structured_adjustment: GridAdjustment


class ExtractedNoOp(ExtractedBase):
    directive_type: Literal["no_op"]
    structured_adjustment: None


class Extraction(StrictModel):
    directives: Annotated[list[Union[
        ExtractedSolar, ExtractedReserve, ExtractedNoCharge,
        ExtractedNoDischarge, ExtractedGrid, ExtractedNoOp,
    ]], Field(min_length=1, max_length=3)]


class PlanHour(StrictModel):
    hour: HourIndex
    grid_kwh: NonNegative
    solar_used_kwh: NonNegative
    battery_action: Literal["charge", "discharge", "idle"]
    battery_kwh: NonNegative
    battery_energy_after_kwh: NonNegative


class OptimizationResponse(StrictModel):
    scenario_id: NonEmpty
    directive_interpretation: Annotated[list[Directive], Field(min_length=1, max_length=3)]
    hourly_plan: Annotated[list[PlanHour], Field(min_length=24, max_length=24)]
    total_grid_kwh: NonNegative
    total_cost_bdt: NonNegative
    peak_grid_kwh: NonNegative
    plan_summary: NonEmpty
