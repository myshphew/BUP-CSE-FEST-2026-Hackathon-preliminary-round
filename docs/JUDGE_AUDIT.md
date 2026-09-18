# Independent engineering audit against the organizer documents

Audit date: 2026-09-18. This is a provisional evidence review, not an official judge score. The main problem (14 pages) was read first, followed by the participant guide/rubric (11 pages); rubric pages 7 and 8 were also inspected visually. Hidden test data is unavailable.

The subsequently supplied text excerpts (guide sections 07–11 and main problem sections 01–12) were checked against this audit and the implementation. They agree with the covered requirements. Both the pasted text and the visually checked original rubric page 7 truncate the last zero-optimum sentence after `quality_ratio`; do not invent its missing text. The printed ratio formula and explicit both-zero rule remain readable. The expanded README now contains every documentation scoring item directly, exact directive/API fields, operational thresholds and both immutable image commands. Its source quickstart selects the candidate branch explicitly. Hosting suggestions are recorded separately in [FREE_HOSTING.md](FREE_HOSTING.md); none has been provisioned.

## Verdict

The required LLM-to-validator-to-optimizer-to-replay architecture is present. Every official cost equals the organizer optimum. A cheaper valid electricity bill cannot be obtained on those same inputs under the same constraints. The new 1.0.1 candidate preserves the primary cost objective and minimizes peak import among cost-optimal schedules. This improves an operational metric without falsely claiming extra cost-score points.

The strongest unresolved risks concern availability and submission access, not the mathematical objective: Render Free can suspend the service, the repository is private, the video is in a draft release, the organizer submission URL is missing, and timing compliance is unresolved. Both PDFs state a 7 PM–11 PM round; the user previously reported 10 PM. The actual applicable deadline/date and policy on updates must be established with the organizers. No official submission has been made by this agent.

## Every scored criterion

“Supported” means the implementation and available tests support the criterion; it is not an award of hidden-test marks. Points are the rubric's available marks.

| Criterion | Points | Judge-style finding and evidence |
|---|---:|---|
| Relevance / no_op | 5 | Supported. Real OpenAI interpretation; irrelevant administration, historical reports and future non-operational notes tested. Failures are never turned into no_op. |
| Directive type | 5 | Supported. Six exact supported types; runtime schema rejects unsupported types. |
| Affected hours | 5 | Supported. Start-inclusive/end-exclusive windows, AM/PM, noon, listed hourly slots, sorted unique hours. Hidden language remains unverified. |
| Numeric values / adjustment shape | 5 | Supported. Remaining fraction versus reduction, fractions, numeric words, capacity-based reserve percentages; finite bounds and exact shapes enforced. |
| Paraphrase robustness | 5 | Supported on the tested set. Terra none/low and Sol low each passed 56/56 live audit requests; no evidence that any is perfect on unseen notes. |
| Ground-truth directive application | 10 | Supported. All five constraints and deterministic overlaps; public evaluation replays against organizer interpretations, not just the model's claimed meaning. |
| Hourly balance / effective solar | 5 | Supported. Equality balance, solar bounds, curtailment and no export in both LP and independent replay. |
| Battery transitions / bounds / rates | 5 | Supported. Signed net flow, after-hour reserves, capacity and rate limits. Additional independent quarter-kWh DP tests cover directive combinations. |
| Action consistency / neutrality / non-negativity | 5 | Supported. One action per hour; idle magnitude zero; final energy equals initial; strict finite non-negative output fields. |
| Optimization quality | 10 | Supported on all ten official cases: zero BDT cost gap, quality ratio 1 on each. Exact LP rather than a greedy heuristic. Invalid schedules receive no claimed credit. |
| Endpoints / HTTP status behavior | 2 | Supported. Exact GET /health and POST /optimize-energy, 200 successes, controlled 400/422/500 errors. |
| Request validation | 2 | Supported. Exactly 24 unique hours, 1–3 non-empty notes, consistent battery, strict numeric types and forbidden extra fields. |
| Interpretation schema / order / types | 3 | Supported. Exactly one ordered entry per note, correct applies/null semantics; malformed model data cannot reach the solver. |
| Plan / top-level schema / scenario echo | 3 | Supported. All required fields, 24 sorted rows, original scenario_id and recalculated totals. |
| Health readiness | 2 | Startup/CBC and actual deployed readiness verified. Health checks configured key presence, not funded quota; real optimization smoke tests establish provider access. Free-host wake-up remains a risk. |
| p95 latency | 3 | Existing public 1.0.0: 30/30 uncached requests, p95 2.642 s. Candidate measurements are recorded separately. Each future judge run determines its own latency marks. |
| Valid-request stability / failure rate | 3 | Repeated public and local live requests passed after key correction. Provider availability/quota and Render idle cold starts remain external risks. |
| Controlled errors / secret safety | 2 | Supported. Fixed public errors, no raw key/body/prompt/traceback logging, validated cache, no invented fallback directives. Candidate adds one bounded transient retry inside the same 20-second model deadline. |
| Live endpoint reachability | 3 | Public HTTPS works without authentication. Continuous availability cannot be guaranteed on Render Free; its documented idle suspension can exceed the request timeout. |
| Pullable Docker fallback / health | 4 | Published 1.0.0 exact digest passed anonymous pull, execution, CBC, health and real model checks. Candidate 1.0.1 also passed anonymous pull, ten offline cases and a real model request; [exact reference](RELEASE_1_0_1.md). No baked-in key; UID 10001. |
| Clean startup / reproducibility | 2 | Pinned dependencies, Docker build, local quickstart and CI. Submitted source version, image and documentation must be identified explicitly. |
| No judge debugging required | 1 | App and image work with configured credentials. Missing public repository/video access and any unpublished image are completion blockers, not tasks to leave for judges. |
| Clean local quickstart | 3 | README documents clone, Python environment, installation, configuration, start and sample verification. Fresh Docker/Linux execution is tested. |
| Environment / model / provider documentation | 2 | Names and meanings documented; no secret values. Astra/low baseline and tested Terra profiles distinguished. |
| Public sample procedure / expected result | 2 | Unmodified authoritative JSON, protected SHA-256, extraction and HTTP evaluator; SAMPLE-01 expected cost 38,365 BDT. |
| LLM / guardrail / optimizer explanation | 1 | Documented module boundaries, LP equations, interpretation provenance and independent replay. |
| Docker pull / run instructions | 1 | README includes exact verified 1.0.0 and 1.0.1 immutable pull/run commands plus health and real-sample verification; no registry placeholders are needed. |
| Dependencies / limitations / secrets | 1 | Pinned/credited libraries, API environment secret, AI assistance attribution, semantic uncertainty and free-host limitations documented. |

The seven category ceilings are 25 + 25 + 10 + 10 + 10 + 10 + 10 = 100. Reporting “100/100” from public tests would be unjustified. Deployment/access conditions must be resolved even if all code tests pass.

## Main problem coverage

| Problem section | Implementation and check |
|---|---|
| 02–03: required LLM pipeline | `main.py` calls real `OpenAIInterpreter`, then directive validation, CBC and independent replay. |
| 04: six directive types | Typed extraction/public unions in `models.py`; prompt semantics in `interpreter.py`. |
| 05.1: one entry, order, applicable/no_op, whole-hour windows | `validator.py`, strict models and live semantic tests. Every cached interpretation originated in a successful real model call. |
| 05.2: total grid electricity cost | `sum(grid_kwh * tariff)` is the primary LP objective. No peak weight or LLM estimate changes it. |
| 05.3: deterministic directive effects | `constraints.py`: solar factors multiply, reserves maximize, grid caps minimize, prohibited rates zero. |
| 06–07: endpoints, status codes and input schema | FastAPI routes and strict Pydantic request models, tested over actual HTTP. |
| 08: guardrails and safe failures | Exact allowed fields/types/ranges/mappings; capacity-dependent reserve validation; controlled errors. |
| 09: battery / solar / energy rules | Lossless signed flow, after-hour state constraints, curtailment, no export, neutrality. Independent replay reconstructs effects separately. |
| 10: complete response schema | Exact required interpretation fields, hourly rows, totals, peak and short deterministic summary. |
| 11: ground-truth checks / tolerance | Evaluator uses official expected semantics; 0.01 absolute kWh/BDT tolerance; official file never changed. |
| 12: canonical specification | Main PDF governs behavior; guide governs deployment, scoring, eligibility and submission. |

No additional LLM calls are required for bills, optimality, summaries or replay. More LLM use in those steps would add uncertainty without satisfying another rubric requirement. Cache hits reuse validated model interpretations; they do not look up organizer answers. The production API never reads the official sample pack.

## Cost-optimality argument and improvement

The LP variables are hourly grid, usable solar, signed battery flow and after-hour stored energy. Each legal schedule gives a feasible LP point, and each feasible LP point maps to one allowed charge/discharge/idle action per hour. All required physical/directive constraints are linear for the specified lossless battery. A globally optimal LP result therefore minimizes the specified bill, subject to numerical tolerance and correct interpretation. The implementation accepts only optimal CBC status and then independently replays the emitted schedule.

Additional audit tests independently enumerate battery states for 48 quarter-kWh unit variants with overlapping factors, reserves, caps and blocked actions, including infeasible combinations. They do not reuse the constraint compiler. The existing 12 independent integer DP comparisons remain. These variants are test-only and never replace official samples or prove natural-language accuracy.

The candidate solves a second LP with the first minimum bill fixed, minimizing peak grid import. Both solves share the original solver time budget. If the optional second solve fails, times out, increases cost beyond the tighter 0.001 BDT check, or worsens peak, the already-established primary optimum is retained. The final response still passes independent replay. This is not a weighted objective that could sacrifice cost.

| Official case | Minimum bill (BDT), unchanged | Previous peak (kWh) | Refined peak (kWh) |
|---|---:|---:|---:|
| SAMPLE-01 | 38,365 | 187.5 | 175 |
| SAMPLE-02 | 42,885 | 180 | 180 |
| SAMPLE-03 | 35,480 | 205 | 205 |
| SAMPLE-04 | 40,495 | 225 | 225 |
| SAMPLE-05 | 33,950 | 175 | 175 |
| SAMPLE-06 | 34,090 | 175 | 175 |
| SAMPLE-07 | 38,550 | 185 | 185 |
| SAMPLE-08 | 37,665 | 210 | 210 |
| SAMPLE-09 | 34,873 | 187 | 170 |
| SAMPLE-10 | 41,620 | 190 | 190 |

Peak reductions are 6.67% and 9.09% on cases 01 and 09 respectively. They do not lower an already optimal electricity bill and do not automatically earn additional rubric marks. They demonstrate a useful operational tie-break among equally cheap schedules. Reducing demand, inventing solar, relaxing reserves, spending the starting battery or exploiting tolerance would invalidate the result.

## Terra reasoning decision

| Profile | Paraphrase/injection requests | p95 | Harder wording/order requests | p95 |
|---|---:|---:|---:|---:|
| Terra / none | 30/30 | 2.825 s | 26/26 | 2.919 s |
| Terra / low | 30/30 | 2.463 s | 26/26 | 3.014 s |
| Sol / low | 30/30 | 4.171 s | 26/26 | 2.958 s |

Requests used the real production API pipeline in-process with application caching disabled and rotating candidate order. Times include the real model call and math/replay, but exclude public hosting. Different finite runs are not proof of universal speed differences. Stress-set maximums were 6.804 s, 3.423 s and 3.013 s respectively. Full reports are stored separately from organizer data.

Terra is the configured model, not “Terry.” OpenAI documents Terra as a balanced model, not the strongest overall reasoning model. Both `none` and `low` are supported. `none` still uses the generative model to interpret language; it does not turn the application into phrase matching. `low` permits additional reasoning but cannot guarantee perfect semantics. Sol is the stronger general-purpose tier; this task's measured accuracy did not improve when switching to it.

For an accuracy-first submission, Terra/low is a reasonable candidate if its final hosted benchmark remains below the five-second p95 target. No observed accuracy improvement over none is claimed. The language task is compact; the deterministic solver supplies all mathematical optimization regardless of reasoning effort.

Official sources: [Terra model](https://developers.openai.com/api/docs/models/gpt-5.6-terra), [Sol model](https://developers.openai.com/api/docs/models/gpt-5.6-sol), [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning), [Render Free limits](https://render.com/docs/free).

## What actually makes the submission competitive

1. Reliable semantic extraction and correct ground-truth application protect the largest 50-point share and all downstream optimization credit.
2. Proven minimum electricity cost gives the full available cost ratio on the known cases; the same-cost lower peak is an engineering improvement.
3. Independent replay, independent DP cost checks, safe transient retries and honest live tests are concrete verification evidence.
4. A clear video explaining why the LLM handles language and the LP handles cost matters first when total scores tie. More UI, more model calls or inflated confidence does not create rubric points.
5. Public artifact access and continuous endpoint/model availability can decide qualification even when the algorithm is strong.

## Candidate execution evidence

The 1.0.1 candidate passed 243 tests on Windows and 243 inside Linux. Terra/low over real Docker HTTP passed 30/30 uncached official requests with p95 2.673 seconds and maximum 2.774 seconds. All ten official cases also passed with up to eight concurrent requests (maximum 2.952 seconds). The updated 2:38 video was visually reviewed and fully decoded. Publication and local runtime checks are recorded in [audit-verification.json](audit-verification.json); deployment steps are in [RELEASE_1_0_1.md](RELEASE_1_0_1.md).

Selected Terra/low additionally passed 9/9 explicitly labeled semantic-edge unit variants: one/two/three no-op-only notes, midnight start/end, all-day and disjoint windows, an only-allowed charging window, and all-day capacity percentage reserve. These checks compare exact semantics and physical replay; no organizer-reference optimal cost is claimed for the variants.

The current public 1.0.0 service was also checked after a long interval without agent traffic: `/health` returned HTTP 200 in 22.120 seconds. Platform spin-down was not independently confirmed, so this is an observed delayed health request, not a guaranteed cold-start bound. It does not remove Render Free's documented suspension risk.

After that delayed health check, the existing public 1.0.0 service passed a fresh official SAMPLE-01 request in 6.869 seconds with the correct 38,365 BDT cost. This one request is reported separately from the earlier 30-request hosted benchmark; its latency is not a new representative p95 estimate.

## README and pasted-requirements follow-up

After updating the documentation, the existing Windows environment again passed 243 tests (two upstream warnings), dependency checks and all ten official offline cases. The documented local health, extraction, curl POST and sample-evaluator commands succeeded; SAMPLE-01 retained the 38,365 BDT bill and 175 kWh peak. The running service had cache enabled, so these smoke checks are not new uncached language/latency evidence. All 51 checked local documentation links/anchors resolved; fences and a key-pattern scan passed; the official sample SHA-256 remained unchanged. No runtime code, hosting settings or monitoring services were changed by this follow-up.
