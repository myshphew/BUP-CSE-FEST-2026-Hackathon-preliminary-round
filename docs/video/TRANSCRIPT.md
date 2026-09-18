# Solution video transcript

Narration is synthesized using the installed Microsoft David voice. API examples are recorded version 1.0.1 container results; they are not a hosted 1.0.1 benchmark.

## Scene 1

GridWise turns twenty four hours of demand, solar forecasts, electricity tariffs, a battery, and operator notes into a valid minimum cost plan. Correctness comes first. Every operational instruction must be interpreted and applied, every hour must balance, and the battery must return to its initial energy at day end. Our objective is the campus electricity bill, not model token cost.

## Scene 2

The architecture separates language from mathematics. OpenAI Terra interprets all notes in one structured response. Deterministic Python guardrails validate note mappings, types, hours, and numeric bounds. CBC solves the resulting linear program. A separate validator reconstructs the rules and replays every returned hour. The language model never calculates schedules, battery trajectories, totals, or bills.

## Scene 3

This example is an actual version one point zero point one container response using the unchanged official sample. Panel cleaning leaves twenty five percent of forecast solar between noon and two PM. That means hours twelve and thirteen, factor zero point two five. The unrelated registration note becomes no operation. Validation rejects invented fields or invalid directives; provider failure is never silently changed into no operation.

## Scene 4

The first linear program proves the minimum electricity cost. A second solve keeps that bill fixed and minimizes peak grid import among equally cheap schedules. For sample one, peak import falls from one hundred eighty seven point five to one hundred seventy five kilowatt-hours, while the bill remains thirty eight thousand three hundred sixty five taka. Hard constraints and independent replay remain mandatory. If optional refinement fails, the proven primary optimum is retained.

## Scene 5

All two hundred forty three tests passed on Windows and inside Linux Docker. The official minimum costs still match in all ten cases. Independent dynamic programming checks additional directive combinations. Thirty uncached real model requests passed, and all ten cases also passed with up to eight concurrent requests. Terra with no reasoning, Terra with low reasoning, and Sol with low reasoning each passed fifty six language checks. These finite tests cannot prove hidden-case perfection.

## Scene 6

Docker runs the API as an unprivileged user. Credentials are injected only at runtime. The README supplies exact pull and run commands, a health check, and an official sample command. The returned sample one plan contains twenty four independently verified rows. Errors contain fixed safe messages. One short retry can recover a transient provider failure within the existing deadline; invalid credentials and insufficient quota are not retried.

## Scene 7

The candidate uses Terra with low reasoning and a normal cache of one hundred twenty eight successful interpretations. Uncached container p ninety five was two point six seven seconds. Low reasoning is a measured option, not a promise of perfect language understanding. The exact image and verification reports support reproducibility. Free hosting can sleep after inactivity, so continuous availability and accessible submission artifacts still matter during judging.

