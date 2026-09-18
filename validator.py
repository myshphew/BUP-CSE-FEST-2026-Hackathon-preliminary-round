"""Deterministic guardrails between the language model and the optimizer."""

import json

from pydantic import ValidationError

from errors import InterpretationError
from models import Directive, Interpretation, Scenario


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
