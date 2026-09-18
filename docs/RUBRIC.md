# Rubric alignment

Source: supplied Participant Guide, sections 06–10, especially pages 7–8. Alignment describes implementation and evidence, not awarded points or guaranteed hidden-case performance.

| Category | Points | Implementation and evidence | Remaining verification |
|---|---:|---|---|
| LLM directive interpretation | 25 | Real Responses API path; strict schemas; Astra/Sol/Terra each passed 30/30 official live requests; Astra/Terra each passed 15/15 supplemental language checks | Unseen-note accuracy |
| Directive application and constraint correctness | 25 | All five operational directives; deterministic overlap rules; energy/battery equations; independent replay; public-case and mutation tests | Hidden-case evaluation |
| Optimization quality | 10 | Exact lossless-battery LP; proven optimal CBC status; all 10 public optimal costs matched, including 30/30 real container requests; 12 independent small-instance DP comparisons | Hidden-case evaluation |
| API contract and schema | 10 | Exact endpoints/fields; strict validation; ordered note mappings and plans; scenario echo; 400/422/500 controlled errors; HTTP tests | External deployed endpoint checks |
| Performance and reliability | 10 | Bounded deadlines/concurrency, safe failures, validated cache; real uncached Docker HTTP 30/30 passed, p95 3.667s, max 5.024s | Hosted p95, continuing quota/account availability, deployment failure rate |
| Deployment and Docker fallback | 10 | Verified Linux build/run, 165 container tests, non-root execution, no baked secrets, health check, Compose startup, exported image, passing remote CI | Exact published image tag/digest, anonymous pull, external hosted availability |
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
