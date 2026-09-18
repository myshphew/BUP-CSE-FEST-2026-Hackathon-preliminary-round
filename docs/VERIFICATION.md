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
| `python -m pytest -q` | 150 passed at this verification stage; two upstream dependency deprecation warnings |
| Official offline runner | 10/10 passed; all optimal costs match exactly; one run p95 0.023 seconds |
| Independent optimum oracle | 12 integer-input unit variants agree with a separate dynamic-programming implementation |
| Real production Uvicorn, missing key | `/health` and valid `/optimize-energy` safely return HTTP 500 `service_not_ready`; malformed JSON returns 400 |
| Real Uvicorn with test-only interpretation injection | `/health` returns 200; 30/30 official requests pass across three repetitions; one run p95 approximately 0.015 seconds |
| OpenAI SDK integration | Request serialization, valid output, cache behavior, refusal, incomplete/malformed output, 401/404/429/5xx, timeout, and prompt/data separation tested with HTTPX transport interception |
| Public deployment / registry mutation | Not performed |

The successful offline and fixture HTTP tests supply organizer expected interpretations; **they do not evaluate real model understanding**. The provider mock is intercepting the real SDK transport, not calling OpenAI. Test-only fixture modules are excluded from Docker.

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

- No `OPENAI_API_KEY` was configured: account/model access, live extraction accuracy, provider quota, and end-to-end p95 remain untested.
- No Docker CLI/daemon was installed: the Dockerfile and CI commands are prepared, but Linux container build, solver compatibility, and pull/run readiness have not been executed locally.
- CI has not been run remotely; source changes have not been pushed or deployed.
- A public base URL, published pullable image, independent fresh-machine check, and recorded three-minute video are not yet available.

Reproduce locally with the README commands. Generated detailed reports are in ignored `output/`; they are evidence from individual runs, not official judge results. Update this file after live/container/deployment verification rather than treating planned checks as completed.
