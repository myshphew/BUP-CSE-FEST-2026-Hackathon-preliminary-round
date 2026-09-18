# Local verification evidence

Date: 2026-09-18. Host: Windows x64. Runtime: Python 3.12.14 in `.venv`, created using the available Codex workspace runtime because the system default Python is 3.10. Install Python 3.11+ on a clean machine before recreating this environment. Packages are pinned in `requirements.txt` and `requirements.lock`.

## Observed results

| Check | Actual result |
|---|---|
| Repository inspection | Initially only the existing `AGENTS.md` and empty README; no implementation to preserve |
| Source review | Main problem PDF read first, then participant guide; relevant constraint/scoring pages rendered and inspected |
| Official sample preservation | Source and root copy SHA-256 match `fa6abd71868e0faf429a87429d7d4a2b7bfd38c5551565637498d7fec68d5f32`; regression test protects it |
| Dependency installation | Installed successfully into isolated Python 3.12 environment |
| `pip check` | No broken requirements found |
| CBC availability | Bundled executable ran startup LP and all test optimization problems |
| `python -m pytest -q` | 165 passed after latency/cache changes; two upstream dependency deprecation warnings |
| Official offline runner | 10/10 passed; all optimal costs match exactly; one run p95 0.023 seconds |
| Independent optimum oracle | 12 integer-input unit variants agree with a separate dynamic-programming implementation |
| Real production Uvicorn, missing key | `/health` and valid `/optimize-energy` safely return HTTP 500 `service_not_ready`; malformed JSON returns 400 |
| Real Uvicorn with test-only interpretation injection | `/health` returns 200; 30/30 official requests pass across three repetitions; one run p95 approximately 0.015 seconds |
| OpenAI SDK integration | Request serialization, valid output, cache behavior, refusal, incomplete/malformed output, 401/404/429/5xx, timeout, and prompt/data separation tested with HTTPX transport interception |
| User's original real HTTP benchmark | 30/30 passed on Astra/low; uncached p95 5.970179 seconds, max 6.815103 seconds; saved report inspected locally |
| Live model comparison after compact extraction | Astra/low 30/30, p95 4.950s; Sol/none 30/30, p95 3.779s; Terra/none 30/30, p95 3.592s; all application caches disabled |
| Supplemental live language checks | Astra/low and Terra/none each passed 15/15: ten paraphrases plus five appended instruction-injection variants; separate from the official JSON |
| Selected Terra/none profile over real HTTP | 30/30 passed with cache disabled; p95 3.005 seconds; temporary Uvicorn server stopped afterward |
| Running local production API | Restarted on port 8000 with Terra/none and cache 128; health 200; correct first request about 2.679 seconds and cached repeat about 0.013 seconds |
| Cache concurrency and cancellation | Identical concurrent misses share one call; one canceled caller does not cancel another; disabled-cache calls stay independent; all covered by tests |
| Docker build | Successful Linux/amd64 build on Docker Engine 29.8.0; pinned dependencies installed; bundled CBC works |
| Linux container tests | 165 passed in 2.03 seconds; two upstream deprecation warnings; tests mounted read-only into a disposable container |
| Container offline samples | 10/10 optimal costs and independent replay passed |
| Container real OpenAI HTTP benchmark | Terra/none, cache 0: 30/30 passed; p95 3.667017 seconds; maximum 5.024275 seconds |
| Image contents and runtime | UID 10001; no `/app/.env`; no test fixtures; official sample SHA-256 preserved; `pip check` passed |
| Container invalid inputs and missing secret | Malformed JSON, missing hour, and extra field return 400; missing-key health/optimization both return safe 500 `service_not_ready` |
| Docker Compose | Configuration validated; detached startup with `--wait` passed; current service healthy at port 8000, Terra/none, cache 128 |
| Current Compose real request/cache | SAMPLE-01 correct; first request 2.384 seconds; cached repeat 0.007 seconds |
| Remote CI | Existing commit c9f0040 run verified successful; [GitHub Actions evidence](https://github.com/myshphew/BUP-CSE-FEST-2026-Hackathon-preliminary-round/actions/runs/35361197350) |
| Submission video | Narrated 1080p H.264/AAC MP4, 2:44; frames visually inspected; full audio/video decode passed; uses recorded local results |
| Local image archive | Exported Docker image to `output/submission/gridwise-1.0.0.tar`; checksums and submission manifest generated |
| Archive and workflow checks | Docker archive loaded successfully; source ZIP integrity passed and excludes `.env`; both GitHub workflows pass actionlint/ShellCheck; Compose configuration validates |
| Public deployment / registry mutation | Not performed |

The offline and fixture HTTP tests supply organizer expected interpretations; **those rows do not evaluate real model understanding**. The additional live-comparison and language-check rows use genuine OpenAI calls with the configured local key. No key is included in reports. The live comparison runs the production FastAPI pipeline in-process; verify the final profile over TCP as documented in [performance results](PERFORMANCE.md). Test-only fixture modules are excluded from Docker.

## Public optimal costs

| Case | Organizer cost (BDT) | Computed cost (BDT) |
|---|---:|---:|
| SAMPLE-01 | 38365 | 38365 |
| SAMPLE-02 | 42885 | 42885 |
| SAMPLE-03 | 35480 | 35480 |
| SAMPLE-04 | 40495 | 40495 |
| SAMPLE-05 | 33950 | 33950 |
| SAMPLE-06 | 34090 | 34090 |
| SAMPLE-07 | 38550 | 38550 |
| SAMPLE-08 | 37665 | 37665 |
| SAMPLE-09 | 34873 | 34873 |
| SAMPLE-10 | 41620 | 41620 |

Every computed schedule also passed independent replay under the official interpretations. Identical cost does not require identical action sequences.

## Not yet verified

- OpenAI access and the documented live tests have passed, but finite public/supplemental tests cannot establish perfect accuracy on hidden notes or guarantee future provider latency/quota.
- Public hosting, anonymous registry pulls, and an independent external-network request are not yet verified. The local archive is not a substitute for the required pullable registry reference.
- The existing CI passed, but the new manual publishing workflow and documentation/Compose changes are local and have not been pushed. The publishing workflow has not run.
- The 2:44 video is created locally but still needs organizer-accessible upload/submission.
- GitHub metadata reports the repository is currently public, created at 2026-09-18T13:13:45Z. The question-reveal/deadline times were not supplied, so event timing compliance cannot be determined. The connected account cannot change repository visibility.

Reproduce locally with the README commands. Generated detailed reports are in ignored `output/`; they are evidence from individual runs, not official judge results. Update this file after live/container/deployment verification rather than treating planned checks as completed.
