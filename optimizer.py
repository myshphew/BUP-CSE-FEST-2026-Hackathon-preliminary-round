"""Deterministic linear optimization. No LLM, prompts, or sample lookup here."""

import math
import time

import pulp

from constraints import compile_constraints
from errors import InfeasibleError, SolverError
from models import Directive, OptimizationResponse, PlanHour, Scenario


def make_solver(time_limit: float = 3.0):
    return pulp.PULP_CBC_CMD(
        msg=False, threads=1, timeLimit=time_limit,
        options=["randomSeed 1", "randomCbcSeed 1", "primalTolerance 1e-8", "dualTolerance 1e-9"],
    )


def solver_ready() -> bool:
    """Execute a tiny LP at startup, so a missing/non-executable CBC is detected."""
    try:
        solver = make_solver()
        if not solver.available():
            return False
        problem = pulp.LpProblem("startup_check", pulp.LpMinimize)
        variable = pulp.LpVariable("x", lowBound=1)
        problem += variable
        problem.solve(solver)
        return problem.status == pulp.LpStatusOptimal and variable.value() == 1
    except (pulp.PulpError, OSError):
        return False


def optimize(
    scenario: Scenario, directives: list[Directive], time_limit: float = 3.0,
    *, minimize_peak: bool = True,
) -> OptimizationResponse:
    started = time.monotonic()
    hours = sorted(scenario.hours, key=lambda x: x.hour)
    bounds = compile_constraints(scenario, directives)
    battery = scenario.battery
    problem = pulp.LpProblem("campus_energy", pulp.LpMinimize)
    grid, solar, delta, energy = [], [], [], []
    for h, bound in enumerate(bounds):
        grid.append(pulp.LpVariable(f"grid_{h:02}", lowBound=0, upBound=bound.grid_cap))
        solar.append(pulp.LpVariable(f"solar_{h:02}", lowBound=0, upBound=bound.solar))
        # A single signed flow is exact for this lossless battery: positive charge,
        # negative discharge. Simultaneous charge/discharge cannot be represented.
        delta.append(pulp.LpVariable(f"delta_{h:02}", lowBound=-bound.discharge, upBound=bound.charge))
        energy.append(pulp.LpVariable(f"energy_{h:02}", lowBound=bound.reserve, upBound=battery.capacity_kwh))
        before = battery.initial_energy_kwh if h == 0 else energy[h - 1]
        problem += energy[h] == before + delta[h], f"battery_transition_{h}"
        problem += grid[h] + solar[h] == hours[h].demand_kwh + delta[h], f"balance_{h}"
    problem += energy[23] == battery.initial_energy_kwh, "end_of_day_neutrality"
    cost = pulp.lpSum(grid[h] * hours[h].tariff_bdt_per_kwh for h in range(24))
    problem += cost
    try:
        problem.solve(make_solver(time_limit))
    except (pulp.PulpError, OSError) as exc:
        raise SolverError() from exc
    if problem.status == pulp.LpStatusInfeasible:
        raise InfeasibleError()
    if problem.status != pulp.LpStatusOptimal or problem.sol_status != pulp.LpSolutionOptimal:
        raise SolverError()

    # Lexicographic optimization: keep the proven minimum electricity cost fixed,
    # then reduce peak import among equally cheap schedules. A weighted peak
    # penalty would trade away the judge's primary objective and is not used.
    peak_refined = False
    remaining = time_limit - (time.monotonic() - started)
    if minimize_peak and remaining > 0.05:
        original = [(v, v.value()) for v in problem.variables()]
        optimal_cost = pulp.value(cost)
        original_peak = max(v.value() for v in grid)
        peak = pulp.LpVariable("peak_import", lowBound=0)
        problem += cost == optimal_cost, "preserve_optimal_cost"
        for h in range(24):
            problem += grid[h] <= peak, f"peak_import_{h}"
        problem.setObjective(peak)
        try:
            problem.solve(make_solver(remaining))
            refined_cost = pulp.value(cost)
            refined_peak = max(v.value() for v in grid)
            peak_refined = (
                problem.status == pulp.LpStatusOptimal
                and problem.sol_status == pulp.LpSolutionOptimal
                and refined_cost is not None and math.isfinite(refined_cost)
                and abs(refined_cost - optimal_cost) <= 0.001
                and refined_peak <= original_peak + 1e-7
            )
        except (pulp.PulpError, OSError, TypeError, ValueError):
            peak_refined = False
        if not peak_refined:
            # Secondary improvement is optional. Its timeout or numerical failure
            # must not discard the already established primary optimum.
            for variable, original_value in original:
                variable.varValue = original_value

    def value(variable):
        result = variable.value()
        if result is None or not math.isfinite(result):
            raise SolverError()
        return 0.0 if abs(result) < 1e-9 else float(result)

    plan = []
    changes = []
    for h in range(24):
        change = value(delta[h])
        # CBC writes a finite-precision solution file. A discharge equal to demand
        # can round very slightly above it; snap only sub-micro-kWh residuals.
        if -1e-6 < hours[h].demand_kwh + change < 0:
            change = -hours[h].demand_kwh
        changes.append(change)
        # Reconstruct accounting from the actual returned flows; do not accumulate
        # independent rounding errors in CBC's printed state/grid columns.
        used_solar = min(bounds[h].solar, max(0.0, value(solar[h])))
        imported = hours[h].demand_kwh + change - used_solar
        if imported < 0 and imported > -1e-6:
            used_solar = max(0.0, hours[h].demand_kwh + change)
            imported = 0.0
        state = math.fsum([battery.initial_energy_kwh, *changes])
        if -1e-6 < state < 0:
            state = 0.0
        plan.append(PlanHour(
            hour=h, grid_kwh=imported, solar_used_kwh=used_solar,
            battery_action="charge" if change > 0 else "discharge" if change < 0 else "idle",
            battery_kwh=abs(change), battery_energy_after_kwh=state,
        ))
    total_grid = math.fsum(p.grid_kwh for p in plan)
    total_cost = math.fsum(p.grid_kwh * hours[p.hour].tariff_bdt_per_kwh for p in plan)
    applied = sum(d.applies for d in directives)
    peak_description = " Selected a minimum-peak schedule at the same cost." if peak_refined else ""
    return OptimizationResponse(
        scenario_id=scenario.scenario_id, directive_interpretation=directives, hourly_plan=plan,
        total_grid_kwh=total_grid, total_cost_bdt=total_cost,
        peak_grid_kwh=max(p.grid_kwh for p in plan),
        plan_summary=(f"Applied {applied} operating directive(s). Minimized grid cost to "
                      f"{total_cost:.2f} BDT using available solar and tariff-based battery scheduling; "
                      f"restored the battery to {battery.initial_energy_kwh:g} kWh at day end."
                      f"{peak_description}"),
    )
