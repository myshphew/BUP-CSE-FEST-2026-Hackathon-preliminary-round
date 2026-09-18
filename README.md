# bup-cse-preliminary-round — GridWise

A FastAPI service for the **BUP CSE Fest 2026 Smart Campus Energy Optimization Challenge**. OpenAI GPT-6 Astra interprets operator notes, deterministic guardrails validate the result, PuLP/CBC minimizes 24-hour grid cost, and an independent validator replays the final schedule before it is returned.

**Verification status:** all 10 official sample optimal costs match. Live OpenAI comparison passed 30/30 requests each for Astra, Sol, and Terra with application caching disabled. Astra and Terra also passed 15/15 supplemental paraphrase/adversarial checks each. The local test suite passes. Public hosting and Docker execution remain unverified; Docker Desktop is installed but a Windows prerequisite is disabled. See [verification evidence](docs/VERIFICATION.md) and [measured model performance](docs/PERFORMANCE.md). These results are not a claimed hidden-judge score.

## Official sources and API permission

The [main problem statement](docs/reference/main_prblm-1.pdf) defines behavior and schemas. The [participant guide and rubric](docs/reference/BUP_CSE_FEST_2026_Participant_Guide__Evaluation_Rubric_GridWise_LLM.pdf) defines scoring, deployment, and submission. The guide, section 04, page 5 explicitly permits **external model APIs or local models**, so OpenAI is allowed. It requires the language model to produce the operator-note interpretation used by the optimizer; phrase matching alone or an AI-written summary is insufficient.

The default model is `gpt-6-astra`, using the OpenAI **Responses API with Structured Outputs**, supported by the [official model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra) and [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs). Your account must have access, funded quota, and adequate rate limits during judging.

The benchmark-selected **lower-latency profile** is `OPENAI_MODEL=gpt-5.6-terra` with `OPENAI_REASONING_EFFORT=none`. Set both variables together to use it. The original Astra/low default remains available as the documented baseline. This profile change affects language interpretation only; optimization and all validators are unchanged.

The root [official sample pack](BUP_CSE_FEST_2026_Preli_Public_Sample_Cases.json) is a byte-for-byte copy of the supplied organizer file, with 10 cases under `cases`. Each contains `input`, `expected_output`, and supporting metadata. Its SHA-256 is:

```text
fa6abd71868e0faf429a87429d7d4a2b7bfd38c5551565637498d7fec68d5f32
```

The service never loads reference interpretations or schedules. They are used only by tests and the explicitly labeled offline evaluation command. Do not edit the official file.

## Clean local quickstart

Install **Python 3.11 or later**; Python 3.12 is the tested version. CBC is included in the pinned PuLP distribution on supported platforms. No database or separate model server is needed.

```bash
git clone https://github.com/myshphew/BUP-CSE-FEST-2026-Hackathon-preliminary-round.git bup-cse-preliminary-round
cd bup-cse-preliminary-round
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell; use py -3.12 instead of python above if your default is older.
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Then install exact runtime versions and development tests:

```bash
python -m pip install -r requirements.lock -r requirements-dev.txt
```

Copy `.env.example` to `.env` (`Copy-Item .env.example .env` in PowerShell; `cp .env.example .env` in Bash). Set `OPENAI_API_KEY` in that local file. Keep the key out of source control, screenshots, terminal output, and public submission fields. All other settings have working defaults.

```bash
python -m pytest -q
python -m scripts.evaluate_samples --offline
python run.py
```

The launcher binds `0.0.0.0:8000`, or the port supplied by `PORT`. Equivalent explicit command:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --no-access-log
```

In another terminal with the virtual environment activated:

```bash
curl http://127.0.0.1:8000/health
python -m scripts.extract_sample --index 1
curl -X POST http://127.0.0.1:8000/optimize-energy -H "Content-Type: application/json" --data-binary "@output/request.json"
python -m scripts.evaluate_samples --url http://127.0.0.1:8000 --limit 1
python -m scripts.evaluate_samples --url http://127.0.0.1:8000 --output output/live-samples.json
```

On Windows use `curl.exe` if PowerShell aliases `curl`. The extraction command copies the first **existing official** input to `output/request.json` and its complete reference response to `output/reference-response.json`; it does not generate scenarios. The ready health response is `{"status":"ok"}`. SAMPLE-01 should return a replay-valid 24-hour plan with `total_cost_bdt = 38365` within 0.01 BDT. Exact battery actions and peak grid may differ between equally optimal solutions.

`/health` verifies that a client is configured and the local solver passed a startup solve. It makes no paid provider call and cannot establish that a key has funded quota or model access. Missing credentials or an unavailable CBC produce controlled HTTP 500 with `service_not_ready`. **A successful full sample request is necessary before declaring a deployment ready for judging.**

## Where the LLM is needed, step by step

1. `main.py` accepts and strictly validates the scenario: 24 distinct hours, 1–3 non-empty notes, finite non-negative numeric values, and consistent battery bounds.
2. `interpreter.py` sends all notes and battery reference values in **one** OpenAI request. It extracts only note indexes, directive types, affected hours, and values. Percentage reserves can use the supplied battery capacity. Notes are user data, never system instructions. The model has no tools, credentials in its prompt, or execution path.
3. `validator.py` validates this compact untrusted extraction, derives `applies` and short explanations deterministically, then revalidates the exact public response shape and scenario-dependent bounds. It rejects unknown types/fields, invalid hours, duplicate or missing note mappings, incorrect `applies` semantics, non-finite numbers, and reserves above capacity. Generating redundant fields in Python reduces model output tokens without removing any semantic checks.
4. `constraints.py` combines overlapping instructions deterministically: multiply solar factors, maximize reserves, minimize grid caps, and zero prohibited charge/discharge limits.
5. `optimizer.py` builds and solves the linear program with CBC. **All schedules, costs, battery states, and grid totals come from deterministic code.** No LLM call is made here.
6. `schedule_validator.py` independently rebuilds the directive effects and replays each hour. It verifies energy balance, solar usage, battery transitions and bounds, rates, windows, grid caps, final neutrality, and recomputed totals.
7. `main.py` returns the exact response schema and a deterministic summary. Provider or validation failure returns a controlled error; it never substitutes `no_op` or serves a reference answer.

```mermaid
flowchart LR
    A[Scenario JSON] --> B[Strict request validation]
    B --> C[OpenAI: interpret notes]
    C --> D[Deterministic directive validation]
    D --> E[PuLP / CBC: minimize grid cost]
    E --> F[Independent schedule replay]
    F --> G[Validated JSON response]
```

This is a single service with separate responsibilities. See [the mathematical formulation and implementation decisions](docs/ARCHITECTURE.md) and [the rubric mapping](docs/RUBRIC.md).

## API contract

- `GET /health`: HTTP 200 with `{"status":"ok"}` when configured and the solver is usable.
- `POST /optimize-energy`: one scenario object, exactly as `cases[i].input` in the official JSON. Do not send the whole sample pack or the case wrapper.
- Success: HTTP 200 with `scenario_id`, `directive_interpretation`, `hourly_plan`, `total_grid_kwh`, `total_cost_bdt`, `peak_grid_kwh`, and `plan_summary`.
- Malformed JSON or an invalid request: HTTP 400. Extra fields and strings/booleans in numeric fields are rejected. Input hours may arrive out of order; responses are always ordered 0–23.
- Infeasible validated constraints: HTTP 422. Feasible organizer scoring cases should never need this path under their correct interpretation.
- Model refusal, incomplete/malformed model output, upstream failure, solver failure, timeout, or failed replay: controlled HTTP 500. Error bodies contain only a fixed code/message, for example `{"error":{"code":"model_unavailable","message":"The language model is unavailable. Please retry later."}}`.

Interactive schema documentation is available at `/docs`. Absolute verification tolerance is **0.01 kWh / 0.01 BDT**, as specified. Required response numeric values remain finite and non-negative; totals are recomputed from the returned flows without rounding to display precision.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | required | Secret for the hosted API; never committed |
| `OPENAI_MODEL` | `gpt-6-astra` | Documented production model; any override needs its own compatibility and accuracy evaluation |
| `OPENAI_REASONING_EFFORT` | `low` | Astra: low, medium, high, xhigh, max. Sol/Terra also support `none`; Astra with `none` is rejected locally |
| `OPENAI_TIMEOUT_SECONDS` | `20` | Hard wall-clock deadline around the model call |
| `OPENAI_MAX_OUTPUT_TOKENS` | `2048` | Budget for the short structured response, including reasoning |
| `REQUEST_TIMEOUT_SECONDS` | `28` | Request processing deadline, including semaphore queue time; must be below 30 |
| `SOLVER_TIMEOUT_SECONDS` | `3` | CBC solve time budget; only proven-optimal results are accepted |
| `MAX_CONCURRENT_REQUESTS` | `8` | Maximum active interpretation/optimization pipelines per worker |
| `INTERPRETATION_CACHE_SIZE` | `128` | Bounded cache of successful validated model responses; `0` disables it |
| `PORT` | `8000` | Port used by `python run.py` and Docker |

`.env` is loaded without overriding existing environment variables. Responses API uses `store=false` and SDK retries are disabled to keep failure latency bounded. Invalid outputs and provider failures are never cached. Cache keys include the exact notes, battery context, prompt, model, and reasoning effort; every cache hit is validated again. Simultaneous identical cache misses share one model call; one client's cancellation does not cancel another's shared request. It is an in-memory cache populated only by actual successful model responses, not a public-case lookup.

Use `INTERPRETATION_CACHE_SIZE=128` in normal operation and `0` for uncached latency measurements. Restart the service after editing `.env`; an already-running process retains its startup settings. Caching accelerates repeated notes with identical battery context, but does not make the first unseen note faster.

## Testing and performance

```bash
python -m pytest -q
python -m scripts.evaluate_samples --offline --output output/offline-samples.json
python tests/live_http_smoke.py
python -m pip check
```

Offline evaluation tests math under organizer interpretations. The HTTP smoke script starts real Uvicorn processes, verifies missing-key failure in the production app, and injects official expected interpretations into a **test-only** app to exercise all public cases over sockets. Neither command measures actual language understanding.

For actual LLM accuracy and latency, configure the key, run the production app, disable the interpretation cache for a cold-request benchmark, and run:

```bash
python -m scripts.evaluate_samples --url http://127.0.0.1:8000 --repeat 3 --output output/live-benchmark.json
```

The runner checks interpretation semantics, replays schedules under **organizer ground truth**, compares recalculated cost, and reports nearest-rank p95. Free-text explanations and exact optimal action sequences are not compared. The guide requires every request within 30 seconds and awards full latency credit at p95 <= 5 seconds. Local solver/mock timings do not establish hosted-model p95. Benchmark quota/rate limits and paraphrase accuracy before submitting.

Compare the configured API account's real model behavior without changing `.env` or restarting your existing server:

```bash
python -m scripts.benchmark_models --repeat 3 --output output/model-comparison.json
python -m scripts.benchmark_models --candidate gpt-6-astra:low --candidate gpt-5.6-terra:none --language-checks --repeat 1 --output output/language-checks.json
python -m scripts.verify_live_http --candidate gpt-5.6-terra:none --repeat 3 --output output/terra-http-benchmark.json
```

These commands make paid OpenAI calls with application caching forced off. The first two run the production FastAPI pipeline in-process. The default comparison tests Astra/low, Sol/none, and Terra/none in rotating order against the unchanged official pack. The second command uses explicitly labeled supplemental paraphrases and instruction-injection variants of those cases; it never changes the official JSON and is not used by production. The final command launches an isolated temporary Uvicorn server and verifies real HTTP latency, then stops it; it does not disturb your running server or edit `.env`. Results and the model decision are documented in [performance verification](docs/PERFORMANCE.md).

Tests also include isolated invalid-input mutations, overlapping directives, zero capacity/rates/tariffs, surplus solar, fractional values, infeasibility, independent dynamic-programming optimality checks, model refusal/timeouts/rate limits, prompt/data separation, corrupted schedules, deterministic repeat solves, and concurrent requests. Unit variants are explicitly test-only and never alter the official sample pack.

## Docker and deployment

The image uses Python 3.12, pinned runtime dependencies, an unprivileged user, a health check, and port 8000. Secrets are excluded from the build context. If Docker Desktop is installed but reports that Virtual Machine Platform is disabled, follow [the Windows prerequisite fix](docs/DOCKER_WINDOWS.md). On a Docker-enabled machine:

```bash
docker build -t bup-cse-preliminary-round:1.0.0 .
docker run --rm bup-cse-preliminary-round:1.0.0 python -m scripts.evaluate_samples --offline
docker run --rm --name gridwise -p 8000:8000 --env-file .env bup-cse-preliminary-round:1.0.0
```

Run the health and full sample HTTP commands above. Do not substitute the test fixture app for `main:app` or `run.py` in a deployment.

Publish to your own registry after testing; the following is a **template**, not an existing published image. Replace `YOUR_NAMESPACE` with the authenticated registry owner and record the actual immutable digest in your submission:

```bash
docker tag bup-cse-preliminary-round:1.0.0 ghcr.io/YOUR_NAMESPACE/bup-cse-preliminary-round:1.0.0
docker push ghcr.io/YOUR_NAMESPACE/bup-cse-preliminary-round:1.0.0
docker pull ghcr.io/YOUR_NAMESPACE/bup-cse-preliminary-round:1.0.0
docker run --rm -p 8000:8000 --env-file .env ghcr.io/YOUR_NAMESPACE/bup-cse-preliminary-round:1.0.0
```

Deploy the same image on a publicly reachable platform with `OPENAI_API_KEY` supplied through its secret manager. Keep both judge endpoints accessible without a login, VPN, or manual action. Verify both endpoints **from outside the development machine** and keep the service and image available throughout evaluation. The included CI workflow performs offline tests and container smoke checks when run on GitHub; it has not been executed remotely as part of the local verification.

The guide also requires the repository visibility/timing rules and a maximum three-minute solution video. See [submission steps and video outline](docs/SUBMISSION.md). No image has been pushed and no public service has been deployed from this workspace.

## Dependencies, attribution, and limitations

Python; FastAPI/Starlette; Uvicorn; Pydantic; the OpenAI Python SDK and Responses API; PuLP and its bundled COIN-OR CBC solver; python-dotenv; HTTPX; and pytest are credited external tools. Transitive dependencies are recorded in `requirements.lock`. OpenAI Codex assisted implementation and verification; the team should review and understand the code before submitting.

- The lossless battery, hourly intervals, no-export rule, and terminal neutrality follow the challenge, not a real-world battery degradation/efficiency model.
- Deterministic guardrails verify shapes and numeric/physical consistency. They cannot prove that a valid-looking interpretation matches the natural-language intent. That requires live language evaluation against expected semantics.
- LLM behavior and provider latency are not deterministic. The scheduling calculation is deterministic for the same validated inputs and pinned runtime. Equivalent optimal schedules can differ across solver versions/platforms.
- Missing keys, inaccessible models, insufficient quota, or invalid model outputs fail safely; there is no heuristic interpreter fallback. A correct but slow/unavailable provider can still lose rubric points.
- Live-model accuracy and local p95 have been measured for the documented cases; unseen-language accuracy and deployed p95 still require ongoing evaluation. Docker/Linux execution, public deployment, registry publication, and the recorded video remain submission steps.
- The installed test dependencies emit two upstream deprecation warnings; the test suite still passes. They concern Starlette's HTTPX test client and AnyIO's portal alias.
