"""Deterministic guardrails between the language model and the optimizer."""

import json

from pydantic import ValidationError

from errors import InterpretationError
from models import Directive, Extraction, Interpretation, Scenario


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def validate_interpretation(raw: object, scenario: Scenario) -> list[Directive]:
    """Reject invalid output; never repair it by discarding directives or using no_op."""
    try:
        if isinstance(raw, str):
            raw = json.loads(raw, object_pairs_hook=_unique_object)
        if isinstance(raw, Interpretation):
            raw = raw.model_dump()
        result = Interpretation.model_validate(raw)
        directives = result.directive_interpretation
        if [d.note_index for d in directives] != list(range(len(scenario.operator_notes))):
            raise ValueError("Every note must appear exactly once in order")
        for directive in directives:
            if directive.directive_type == "minimum_battery_reserve":
                if directive.structured_adjustment.minimum_energy_kwh > scenario.battery.capacity_kwh:
                    raise ValueError("Reserve exceeds capacity")
        return directives
    except (ValidationError, ValueError, TypeError) as exc:
        raise InterpretationError() from exc


def validate_extraction(raw: str, scenario: Scenario) -> dict:
    """Validate compact model output, then derive redundant public response fields."""
    try:
        extracted = Extraction.model_validate(json.loads(raw, object_pairs_hook=_unique_object))
        entries = []
        for directive in extracted.directives:
            entry = directive.model_dump()
            kind = directive.directive_type
            adjustment = entry["structured_adjustment"]
            if adjustment is None:
                explanation = "This note has no supported effect on the current energy schedule."
            else:
                hours = ", ".join(str(h) for h in adjustment["hours"])
                if kind == "solar_reduction":
                    detail = f"Use {adjustment['factor'] * 100:g}% of forecast solar"
                elif kind == "minimum_battery_reserve":
                    detail = f"Keep at least {adjustment['minimum_energy_kwh']:g} kWh in the battery"
                elif kind == "max_grid_window":
                    detail = f"Limit grid import to {adjustment['max_grid_kwh']:g} kWh"
                elif kind == "no_charge_window":
                    detail = "Disable battery charging"
                else:
                    detail = "Disable battery discharging"
                explanation = f"{detail} during hours {hours}."
            entry.update(applies=kind != "no_op", explanation=explanation)
            entries.append(entry)
        result = {"directive_interpretation": entries}
        # This checks exact original note coverage/order and capacity, too. No
        # sorting, missing-note insertion, type coercion, or no_op fallback.
        validate_interpretation(result, scenario)
        return result
    except (ValidationError, ValueError, TypeError) as exc:
        raise InterpretationError() from exc
