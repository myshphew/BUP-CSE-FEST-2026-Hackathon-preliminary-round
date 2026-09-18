# Rubric alignment

Source: supplied Participant Guide, sections 06–10, especially pages 7–8. Alignment describes implementation and evidence, not awarded points or guaranteed hidden-case performance.

| Category | Points | Implementation and evidence | Remaining verification |
|---|---:|---|---|
| LLM directive interpretation | 25 | Real Responses API path; exact schemas; relevance/type/hours/value instructions; percentage and paraphrase handling in the prompt; SDK transport tests | Live model accuracy on all official notes, additional paraphrases, and unseen notes |
| Directive application and constraint correctness | 25 | All five operational directives; deterministic overlap rules; energy/battery equations; independent replay; public-case and mutation tests | Hidden-case evaluation |
| Optimization quality | 10 | Exact lossless-battery LP; proven optimal CBC status; all 10 public optimal costs matched; 12 independent small-instance DP comparisons | End-to-end correctness under actual model interpretations |
| API contract and schema | 10 | Exact endpoints/fields; strict validation; ordered note mappings and plans; scenario echo; 400/422/500 controlled errors; HTTP tests | External deployed endpoint checks |
| Performance and reliability | 10 | Readiness startup solve; async model client; bounded deadlines and concurrency; safe failures; successful-response cache; repeated/concurrent tests | Actual provider p95, funded quota, account limits, deployment failure rate |
| Deployment and Docker fallback | 10 | Dockerfile, non-root execution, pinned dependencies, secret exclusion, health check, port binding, CI container checks, documented pull/run template | Docker build/run on available host, exact published image tag/digest, external availability |
| Documentation and local reproducibility | 10 | README quickstart, model/provider/config, official sample commands, mathematical explanation, limitations, secret handling, credited tools | Independent fresh-machine reproduction and final real registry/base URL details |

The first category splits into five points each for relevance, directive type, affected hours, numeric values/shape, and paraphrase robustness. Validation catches invalid structure and ranges; it does not replace language accuracy testing.

The constraint category splits into ten points for true directive application, five for balance/effective solar, five for battery behavior, and five for actions/neutrality/non-negativity. Both the optimizer and independent replay enforce these requirements. The sample runner replays under organizer expected directives, not merely the model's claims.

Optimization credit applies only after validity. The organizer formula is `min(1, optimal_cost / recalculated_team_cost)`, averaged across optimization cases and multiplied by ten. Zero-cost cases have special handling in the guide. The runner instead reports strict agreement with the public optimal costs within 0.01 BDT; it does not estimate a hidden-judge score.

## Operational targets

- `/health` ready within 60 seconds of startup.
- Every optimization request within 30 seconds.
- p95 <= 5 seconds: full three latency points; 5–15 seconds: two; 15–30 seconds: one.
- No valid-request failures, malformed success bodies, sensitive errors, or missing directives.
- Public service available without authentication and pullable fallback image available through evaluation.

Mocked HTTP or solver-only benchmarks cannot establish the provider latency or language scores. No full-score claim is justified until the deployed LLM path and required artifacts are verified.

The maximum three-minute video carries no base points but is the first tie-breaker. If it does not break the tie, the guide prioritizes constraint correctness, interpretation, optimization, API validity, reliability, documentation, then exceptional engineering.
