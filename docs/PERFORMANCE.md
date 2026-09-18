# Live performance and model decision

Verified on this Windows development host on 2026-09-18, using real OpenAI calls. The authoritative sample file is unchanged. Machine-readable summaries are in [performance-results.json](performance-results.json); complete per-request reports are in ignored `output/`.

## Results with application caching disabled

| Profile | Correct official requests | Median | p95 | Maximum |
|---|---:|---:|---:|---:|
| Original Astra / low, real HTTP (user's saved baseline) | 30/30 | — | 5.970 s | 6.815 s |
| Compact extraction, Astra / low | 30/30 | 3.089 s | 4.950 s | 5.112 s |
| Compact extraction, Sol / none | 30/30 | 2.654 s | 3.779 s | 5.272 s |
| Compact extraction, Terra / none | 30/30 | 2.069 s | 3.592 s | 3.632 s |

The three-candidate comparison used the production FastAPI pipeline in-process, with candidates run sequentially in rotating order. It includes the real OpenAI network call, all application validation, optimization, and replay, but excludes the small local TCP hop. It forces application cache size zero and does not edit `.env`.

A separate verification started a fresh Uvicorn server using **Terra / none** and sent all ten official inputs three times over **real HTTP**, still with cache size zero:

- **30/30 passed**, with correct interpretation semantics, independent ground-truth replay, and optimal cost.
- **p95 3.005 seconds**, compared with the original 5.970 seconds: approximately **50% lower** in these observed runs.
- All requests completed within five seconds in this run.

These are separate finite samples under varying provider/network conditions, not a controlled claim about universal model speed. The rubric's p95 target is met in these local measurements. Public hosting, different load, unseen notes, and future provider conditions must be evaluated separately. Disabling the application result cache does not disable OpenAI's own prompt-prefix caching.

## Supplemental language checks

Astra/low and Terra/none each passed **15/15** additional checks: ten paraphrases of the official notes and five variants that append instructions attempting to override the real operating directive. The energy inputs and expected semantics come from the official cases; the variants are explicitly labeled and never replace or modify the organizer JSON. The production service does not import these fixtures.

Astra's p95 on this set was 3.975 seconds; Terra's was 4.429 seconds. With only 15 observations, nearest-rank p95 is the maximum observation, so this set should be read primarily as a correctness check. It does not prove perfect resistance to all prompt injection or perfect semantic accuracy on hidden notes. Sol was not included in this supplemental set.

## Selected local profile

The local `.env` now contains:

```dotenv
OPENAI_MODEL=gpt-5.6-terra
OPENAI_REASONING_EFFORT=none
INTERPRETATION_CACHE_SIZE=128
```

The project API was restarted on port 8000 with these settings. `/health` returned HTTP 200. A real first SAMPLE-01 request took approximately 2.679 seconds; its cached repetition took approximately 0.013 seconds, with the correct cost both times.

Terra is selected because it passed both correctness sets and offered lower typical latency plus lower documented token prices. The original Astra/low defaults remain available in the versioned configuration as a baseline; set the two model variables together when reproducing the selected profile on another machine. No model switching happens silently on a failure.

The latency reduction combines a smaller output and the selected model profile:

1. The LLM produces only semantic fields: note index, directive type, hours, and values.
2. Python derives `applies` and a short explanation from validated directives.
3. Exact public response fields and all guardrails remain enforced.
4. Successful interpretations are cached for normal operation. Identical concurrent misses share one call; failures are never cached.
5. Optimization, battery trajectory, costs, and totals remain deterministic and unchanged.

OpenAI documents [`none` reasoning for Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol) and [Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra); Astra requires `low` or higher. Its [latency guidance](https://developers.openai.com/api/docs/guides/latency-optimization) recommends reducing generated tokens. No premium Fast mode setting was required for these results.

## Reproduce without disturbing the running API

These commands use the locally configured secret and make paid requests. They do not print it or change production cache settings.

```powershell
.\.venv\Scripts\python.exe -m scripts.benchmark_models --repeat 3 --output output/model-comparison.json
.\.venv\Scripts\python.exe -m scripts.benchmark_models --candidate gpt-6-astra:low --candidate gpt-5.6-terra:none --language-checks --repeat 1 --output output/language-checks.json
.\.venv\Scripts\python.exe -m scripts.verify_live_http --candidate gpt-5.6-terra:none --repeat 3 --output output/terra-http-benchmark.json
```

The final command starts an isolated temporary Uvicorn instance, forces its cache to zero, performs real HTTP verification, writes its model/cache metadata, and stops that temporary process. Keep `INTERPRETATION_CACHE_SIZE=128` in the normal service. If benchmarking an already-running server instead, set its cache to zero and restart it, then restore 128 and restart when finished.

## Verified Docker performance

Docker Engine 29.8.0 now works. A clean Linux/amd64 image build succeeded, and all **165 tests** passed inside that image. A separate real HTTP benchmark through Docker Desktop used Terra/none with application cache **0**: **30/30 passed, p95 3.667017 seconds, maximum 5.024275 seconds**. The complete report is `output/docker-live-benchmark.json`; the versioned summary is [docker-verification.json](docker-verification.json).

The current service runs through Compose at `http://127.0.0.1:8000` with cache **128**. A new SAMPLE-01 request took 2.384 seconds; its cached repeat took 0.007 seconds, both with the correct interpretation and cost. These timings are observations, not a guarantee. The container p95 remains within the rubric's five-second target even though one of the 30 requests exceeded five seconds.

## Verified public Render performance

On 2026-09-18, the public HTTPS API on Render Free (Oregon) passed **30/30** official requests with application cache **0**, Terra/none, and the published 1.0.0 image. **p95: 2.641738 seconds; maximum: 3.379812 seconds.** This includes public-network HTTP transport, the real OpenAI call, deterministic optimization, and independent ground-truth replay. The sample file checksum was verified before evaluation.

An initial smoke request immediately after the corrected-key deployment passed in 8.596 seconds; it is recorded separately from the 30-request benchmark. The benchmark measures a running instance, not wake-up from Render's idle suspension. The earlier attempt with an incorrect hosted key failed; those failures are preserved separately and are not latency evidence for successful requests.

The production cache is restored to 128 after measurement. Results and final deployment checks are in [public-verification.json](public-verification.json), with all 30 observations in [public-live-benchmark.json](public-live-benchmark.json). Successful finite samples do not guarantee hidden-case correctness or future latency. [Render Free](https://render.com/docs/free) sleeps after 15 idle minutes and takes about one minute to resume; a different model or result caching cannot remove that platform limit.

Final organizer submission and public repository/video access remain. See [current next steps](NEXT_STEPS.md).
