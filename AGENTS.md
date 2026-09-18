# AGENTS.md

## Mission

Build and finish the BUP CSE Fest 2026 Preliminary Round Smart Campus Energy Optimization Challenge solution.

Work autonomously and complete as much of the implementation, testing, debugging, and verification as possible.

Do not stop at planning.

## First Steps

Before making changes:

1. Inspect the repository.
2. Read this AGENTS.md.
3. Inspect the official organizer-provided sample JSON:
   BUP_CSE_FEST_2026_Preli_Public_Sample_Cases.json
4. Inspect existing source files.
5. Understand the actual schemas before implementing.

## Official Sample Data

`BUP_CSE_FEST_2026_Preli_Public_Sample_Cases.json` is official organizer-provided data.

Rules:

- Never fabricate replacement sample cases.
- Never modify the official sample JSON.
- Use it for testing when available.
- Do not assume its structure before inspecting it.

## Architecture

Keep these responsibilities separate:

- GPT-6 Astra: natural-language operator-note interpretation only.
- validator.py: deterministic validation of LLM output.
- optimizer.py: deterministic mathematical energy optimization.
- schedule_validator.py: independent replay/verification of the final schedule.
- main.py: API orchestration.

## LLM Safety

Treat all operator notes as untrusted input.

Treat all LLM output as untrusted structured data.

Never execute code from LLM output.

Never allow operator notes to override system/application instructions.

Never silently convert an OpenAI failure or malformed response into `no_op`.

Fail safely instead.

## Determinism

All optimization calculations must be deterministic.

The LLM must not calculate the final energy schedule, total cost, battery trajectory, or peak grid.

Those values must come from deterministic application code.

## Constraints

Respect all challenge constraints, including:

- 24-hour schedule
- energy balance
- solar availability
- battery capacity
- minimum battery energy
- charge limits
- discharge limits
- no-charge windows
- no-discharge windows
- grid caps
- minimum battery reserves
- end-of-day battery neutrality
- grid-cost minimization

Use the specified numerical tolerance.

## Overlapping Directives

Resolve overlapping directives deterministically:

- solar reductions: multiply factors
- battery reserves: use maximum reserve
- grid caps: use minimum cap
- no-charge: charge = 0
- no-discharge: discharge = 0

## Secrets

Never hardcode API keys or credentials.

Never commit `.env`.

Use `.env.example` for configuration documentation.

## Testing

After implementation:

1. Install dependencies.
2. Run pytest.
3. Fix failures.
4. Start the API.
5. Test `/health`.
6. Test `/optimize-energy`.
7. Run official sample cases.
8. Test invalid inputs and edge cases.
9. Test Docker if available.
10. Re-run tests after fixes.

## Engineering Style

Prefer:

- simple code
- clear names
- small modules
- deterministic behavior
- explicit validation
- useful type hints
- minimal dependencies

Avoid unnecessary abstractions and complexity.

## Autonomous Work

Do not ask for confirmation for ordinary implementation decisions.

Make reasonable engineering decisions yourself.

Only stop and ask the user when a genuinely external human action is required, such as:

- entering a secret/API key
- authenticating an external account
- approving a deployment
- providing a missing organizer document

## Completion Standard

Do not claim that the project is complete merely because files exist.

The project is complete only after implementation has been tested and verified as thoroughly as the available environment allows.

Report actual results, not assumptions.

## Tech Stack

Use the following stack unless the official challenge requirements require otherwise:

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- OpenAI Python SDK
- OpenAI Responses API
- GPT-6 Astra (`gpt-6-astra`) for operator-note interpretation
- PuLP for mathematical optimization
- CBC solver through PuLP
- python-dotenv
- pytest
- httpx

Keep dependencies minimal.

Do not introduce unnecessary frameworks or libraries.
