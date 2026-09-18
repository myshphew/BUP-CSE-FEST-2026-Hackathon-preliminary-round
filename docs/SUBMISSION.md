# Final submission checklist

The public Render API passed 30/30 uncached official requests (p95 2.642 seconds); anonymous GHCR pulls are verified. The video is uploaded to a private draft release. Final organizer submission and public repository/video access remain. See [current steps and submission references](NEXT_STEPS.md). Do not submit localhost or the local image tag as public references.

## Prepared and verified locally

- 165 tests pass inside Linux Docker. All ten official costs match.
- Real OpenAI requests through the container: 30/30 pass with cache 0; p95 3.667 seconds.
- Compose runs a healthy API at `http://127.0.0.1:8000`, using Terra/none and cache 128.
- `output/submission/gridwise-solution.mp4`: 2:44 narrated architecture video, 1080p H.264/AAC; visually checked and fully decoded. Uses recorded local results and a synthetic Microsoft David voice.
- `output/submission/gridwise-1.0.0.tar`: exported tested Docker image; load with `docker load -i output/submission/gridwise-1.0.0.tar`.
- `output/submission/gridwise-source.zip`: source, tests, official samples, and documentation, including these local delivery changes; archive integrity checked and `.env` excluded.
- `output/submission/SHA256SUMS.txt` and `submission-manifest.json`: checksums and accurate publication status.
- `output/submission/sample-01-request.json`, `sample-01-live-response.json`, and `health.json`: official input and actual local service responses.
- Manual GHCR publishing workflow, Compose configuration, README, rubric mapping, reports, and [deployment runbook](DEPLOYMENT.md).

Generated files under `output/` are ignored by Git. The video and verification reports have been uploaded to a private draft release; the image was published separately through GHCR. The image archive does not replace the registry requirement.

## External steps still required

1. **Check repository visibility against the event deadline.** The repository is now private. Its owner must keep it private during the event and make it public after the deadline. The connected account cannot change visibility. Question-reveal/deadline times are unknown, so timing compliance is unresolved.
2. **Use the verified fallback image.** The exact published digest in [current steps](NEXT_STEPS.md) passed anonymous pull/run verification.
3. **Use the verified public API.** Render Free is deployed with Terra/none and cache 128. The key is supplied through Render environment secrets. Public uncached evaluation passed 30/30; see [hosted evidence](public-verification.json).
4. **Check availability before judging.** Test from another network. Render Free sleeps after idle, which can exceed the 30-second limit; warm-instance benchmark success does not establish uninterrupted availability.
5. **Upload the video.** Submit the prepared MP4 or an organizer-accessible link. Review the [transcript](video/TRANSCRIPT.md) and ensure the team can explain the implementation.
6. **Submit real references.** Provide the public base URL, repository, README/configuration, pullable image reference, and video. Never put a secret in a public submission field.

## Video contents

| Time | Show and explain |
|---|---|
| 0:00–0:21 | The 24-hour campus problem, inputs, objective, and validity requirements |
| 0:21–0:43 | OpenAI interpretation → strict guardrails → CBC → independent replay |
| 0:43–1:07 | Actual SAMPLE-01 interpretation: solar factor 0.25 at hours 12 and 13, plus no-op |
| 1:07–1:33 | LP formulation, battery neutrality, physical constraints, and overlap rules |
| 1:33–1:57 | Linux tests, official costs, real OpenAI verification, and limitations |
| 1:57–2:20 | Verified Docker command and recorded local health/optimization results |
| 2:20–2:44 | Model/cache configuration, observed latency, and deployment requirements |

Times are rounded to the nearest second. The video makes no claim that a public deployment already exists. Reproduction and narration details are in [video/README.md](video/README.md). It carries no base points but is the first tie-breaker in the guide.
