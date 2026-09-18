# Solution video transcript

Narration is synthesized using the installed Microsoft David voice. API examples are recorded local production-container results, not a public deployment.

## Scene 1

GridWise solves the BUP CSE Fest Smart Campus Energy Optimization Challenge. Given twenty four hours of demand, solar forecasts, electricity prices, a battery, and operator notes, it returns a valid minimum cost energy plan. Operational instructions must be understood before costs are minimized. The final plan balances energy every hour and restores the battery to its initial energy at the end of the day.

## Scene 2

Our architecture separates language understanding from mathematical decisions. The configured OpenAI Terra model interprets all notes in one structured response. Python validates that response, combines overlapping directives, and sends the resulting constraints to the CBC linear programming solver. A separate schedule validator independently replays the answer. The language model never computes the final schedule, battery trajectory, or bill.

## Scene 3

This example comes directly from the unchanged official sample pack and a real container request. The first note leaves twenty five percent of forecast solar available from noon until two PM. The interpretation therefore selects hours twelve and thirteen, with factor zero point two five. The registration deadline note becomes no operation. Strict validation checks types, note order, hours, numeric bounds, and supported directives. Invalid model output fails safely.

## Scene 4

The optimizer minimizes grid electricity multiplied by the hourly tariff. Signed battery flow expresses charging and discharging without unnecessary binary variables. Hard constraints enforce energy balance, solar availability, battery bounds, rate limits, grid caps, reserves, and final neutrality. Overlapping solar factors multiply; reserves use the maximum; grid caps use the minimum. Prohibited charging or discharging is fixed to zero. Only proven optimal solver results are accepted.

## Scene 5

Verification checks both interpretation and the returned schedule against organizer ground truth. All one hundred sixty five tests passed inside Linux Docker. All ten official optimal costs matched. Thirty real OpenAI requests through the container passed with application caching disabled. The independent replay also checks every hourly constraint and recalculates totals. Additional live paraphrase and instruction injection checks passed earlier; these finite tests do not guarantee every unseen note.

## Scene 6

The service runs as an unprivileged Docker user, with secrets supplied only at runtime. Docker Compose starts the API and waits for its health check. This recorded local request returned HTTP two hundred, a twenty four hour plan, and the correct sample one cost of thirty eight thousand three hundred sixty five taka. Malformed requests return controlled errors. Missing credentials fail readiness without exposing secrets or substituting a reference answer.

## Scene 7

The tested profile is OpenAI Terra with no reasoning effort. Container requests had a ninety fifth percentile latency of three point six seven seconds with the application cache disabled. Normal operation uses a bounded cache of one hundred twenty eight successful interpretations. For submission, deploy the same service to a public host, supply the API key through its secret manager, and provide a pullable image reference. Recheck both public endpoints and keep the service available throughout judging.

