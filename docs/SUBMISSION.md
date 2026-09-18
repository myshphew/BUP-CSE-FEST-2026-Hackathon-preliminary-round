# Final submission and demo

The implementation is prepared locally. Actual accounts, model credentials, public deployment, registry publication, and video recording are still needed. Fill in real values only after verifying them; no published endpoint or image is implied by the templates.

## Complete these steps

1. Configure `OPENAI_API_KEY` securely and run `main:app` via `python run.py`.
2. Run all ten samples through the HTTP evaluator and inspect interpretation, replay, and cost results. Run a cold benchmark with `INTERPRETATION_CACHE_SIZE=0`; record actual provider p95 and failures. Evaluate paraphrases without hard-coding them into the interpreter.
3. On a Docker-enabled host, build the image, run the offline container samples, start it with runtime secrets, and run full HTTP samples. Docker Desktop is now installed locally, but its backend reports that Virtual Machine Platform is disabled. Follow [the administrator/restart steps](DOCKER_WINDOWS.md) first; container checks remain incomplete.
4. Push to an authenticated registry and record the real image tag and digest. Pull/run it from a clean environment using the exact documented command. Ensure judges can pull it without private-registry credentials.
5. Deploy that image as one service with port 8000 or platform-provided `PORT`, server-side secrets, and a public base URL. Verify health and optimization from another network. Keep the service running throughout evaluation.
6. Follow the guide's repository policy: repository created after question reveal, private during the event, public after the submission deadline. Current remote visibility/timing has not been verified or changed by this implementation.
7. Record the video below, keep it under three minutes, and make it organizer-accessible. Submit the public base URL, source repository, README/configuration, exact pullable image reference, and video link/upload.

## Three-minute video outline

| Time | Show and explain |
|---|---|
| 0:00–0:25 | The 24-hour campus problem: demand, solar, tariffs, battery, and operational notes; validity before cost |
| 0:25–0:55 | The pipeline diagram; the configured OpenAI model turns notes into six supported directive types; disclose the actual deployed model and reasoning setting |
| 0:55–1:25 | `validator.py`: note mappings, ordered hours, remaining-solar fractions, capacity bounds, prompt/data separation, safe failure |
| 1:25–1:55 | `optimizer.py`: signed battery flow, cost objective, hard constraints, overlapping rules, and end-of-day neutrality |
| 1:55–2:25 | `schedule_validator.py` and actual test output; show sample optimal cost agreement and independent replay |
| 2:25–2:50 | Run `/health` and a real `/optimize-energy` request; show the verified Docker command and public endpoint |
| 2:50–3:00 | State the verified model, latency results, and reproducibility artifacts; do not present mock results as live-model results |

This is a recording outline, not a completed video. The live demonstration should use the deployed production app with genuine model interpretation.
