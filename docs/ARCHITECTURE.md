# Architecture and mathematical formulation

The request schema was taken from the supplied problem PDF and inspected public JSON, not inferred from an unrelated energy API. All source PDFs are preserved in `docs/reference/`; the public JSON is preserved unchanged at the repository root.

## Module boundaries

| Module | Responsibility |
|---|---|
| `models.py` | Strict typed request, directive, and response schemas |
| `interpreter.py` | One OpenAI Responses request to interpret all notes; validated bounded cache |
| `validator.py` | Reject untrusted interpretation JSON that breaks the schema or scenario bounds |
| `constraints.py` | Combine valid directives into hourly solver bounds |
| `optimizer.py` | Build and solve a deterministic cost-minimizing LP |
| `schedule_validator.py` | Independently reconstruct effects and replay the returned schedule |
| `main.py` | Readiness, deadlines, concurrency, error handling, and orchestration |
| `scripts/` | Explicit offline/full-API verification and official sample extraction |

The production modules never import tests or read the sample file. There is no prompt interpreter based on hard-coded public note wording, case IDs, or reference schedules.

## Linear program

For each hour `h`, let `g[h]` be grid import, `s[h]` solar used, `x[h]` signed battery flow, and `e[h]` battery energy after the hour. Positive `x` is charge and negative `x` is discharge. The objective is:

```text
minimize sum(tariff[h] * g[h])
```

Constraints:

```text
g[h] >= 0
0 <= s[h] <= effective_solar[h]
-discharge_limit[h] <= x[h] <= charge_limit[h]
g[h] + s[h] = demand[h] + x[h]
e[h] = (initial_energy if h == 0 else e[h-1]) + x[h]
active_reserve[h] <= e[h] <= capacity
g[h] <= active_grid_cap[h]                 # when a cap exists
e[23] = initial_energy
```

There is no grid export. Solar may be curtailed. The reserve applies to energy **after** each listed hour. The original minimum also constrains the initial state through request validation.

This is an exact LP for the specified battery. Every signed flow maps to exactly one allowed response action. Conversely, every valid schedule gives one such signed flow. No binary variables are needed because the specification assumes a lossless battery and permits a single net action per hour. An efficiency model or separate charge/discharge costs would require reconsidering this formulation.

Overlaps combine in input note order, with solar factors multiplied, reserves maximized, and grid caps minimized. A no-charge directive sets the upper flow bound to zero; a no-discharge directive sets the lower flow bound to zero. Both restrictions at the same hour force idle.

CBC runs with one thread, fixed seeds, fixed variable/constraint ordering, and tight numerical solver tolerances. Only an optimal solver status is accepted. No arbitrary peak-grid penalty is added to the required cost objective. Alternative optimal plans need not match the organizer action sequence or peak exactly.

The solution file has finite precision. Sub-micro-kWh residuals at zero import are corrected to prevent negative solar/grid serialization. Battery states and totals are recalculated from the returned actions/flows. Independent replay still must pass the official absolute 0.01 tolerance. The fractional regression test covers this correction.

## Independent verification

The replay validator intentionally does not call `compile_constraints` or reuse solver variables. It rereads the original scenario and validated directives, reconstructs effective solar and reserves, and directly checks every applicable restriction against the returned rows. Tests inject a deliberately incorrect solar compiler to show that replay catches solver-model mistakes.

The public evaluation runner supplies organizer ground truth separately. Thus a cheap plan under a wrongly reported interpretation does not pass the evaluator merely by agreeing with its own interpretation.

## Language and safety boundary

Structured Outputs restrict the model to a nested union of exact directive schemas. To reduce generation time, the provider emits only note indexes, directive types, and structured adjustments under `directives`. `validator.py` validates this extraction, derives `applies` from the type, and writes a short deterministic explanation of the validated values. It then applies the original public-schema validation. There is no semantic phrase parser or repair of missing/reordered notes in this conversion.

Application validation is still required: provider responses, JSON, and parsed objects are untrusted. Every note must appear once in its original order, with consistent applies/no-op semantics, sorted unique integer hours, and valid finite numbers. Unknown fields cannot modify demand, tariffs, battery settings, or execute code.

Instructions are separate from the user-role JSON carrying notes. No tools or code execution are available to the model. Missing credentials, refusal, incomplete output, unsupported directives, timeout, and provider errors return fixed controlled errors. The API never converts these into irrelevant notes. Unexpected application exceptions are caught before the server can print a sensitive traceback.

This boundary does not provide a mathematical guarantee of semantic accuracy. A model can still produce a well-formed but wrong hour range or factor; only evaluation against intended meaning establishes that part of correctness. Real OpenAI tests are necessary before submission.

## Performance choices

- One batched interpretation call for 1–3 notes, with `low` reasoning for Astra and a compact semantic output. Sol/Terra can also be evaluated with `none` reasoning; the service rejects that unsupported setting for Astra.
- No model-generated summary or schedule.
- Shared asynchronous client, no SDK retries, a 20-second model deadline, and a 28-second application deadline including queue wait.
- Eight concurrent pipelines per worker by default; the solver runs off the event loop.
- At most 128 successful validated interpretation responses cached in memory. Cache hits are revalidated; changed battery context invalidates the key. No failures or sample fixtures are cached. Concurrent identical misses share one model call with cancellation isolation. When the cache is disabled, every request calls the model independently for honest uncached measurements.
- CBC has a three-second solve budget. Canceling an async request does not forcibly terminate an already-running worker thread; its solver has its own bounded execution time.

These choices limit processing overhead. They do not establish the rubric's p95 target for a hosted model or overloaded service; measure the actual deployed path with the cache disabled for cold-request latency.
