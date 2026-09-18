# Deployment and publication runbook

The API is deployed on Render Free at [the public base URL](https://bup-cse-preliminary-round-1-0-0.onrender.com). With application caching disabled, all 30 official requests passed: p95 2.641738 seconds, maximum 3.379812 seconds. The published GHCR image also passed an anonymous pull and execution checks. See [current submission steps](NEXT_STEPS.md) and [public verification evidence](public-verification.json). Local container evidence remains in [docker-verification.json](docker-verification.json).

## Operate the local service

From the repository root, with `.env` configured:

```powershell
docker compose up -d --build --wait
docker compose ps
curl.exe http://127.0.0.1:8000/health
.\.venv\Scripts\python.exe -m scripts.evaluate_samples --url http://127.0.0.1:8000 --limit 1
```

Docker Desktop must be running. Compose restarts unexpectedly stopped containers, rotates logs, and injects `.env` only at runtime. After changing configuration, use `docker compose up -d --force-recreate --wait`. Use `docker compose down` to stop this service. A Docker health check reports readiness but does not itself restart a merely unhealthy process.

The exported image can be transferred to another Docker-enabled computer:

```powershell
docker load -i output/submission/gridwise-1.0.0.tar
docker run --rm -p 8000:8000 --env-file .env bup-cse-preliminary-round:1.0.0
```

Supply the receiving computer's own `.env` securely. The archive contains no baked-in key. Checksums are in `output/submission/SHA256SUMS.txt`.

## Publish through GitHub Container Registry

The prepared `.github/workflows/publish-image.yml` uses the existing GitHub repository without adding Docker Hub credentials. It follows [GitHub's documented job-token registry authentication](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images). It is manual; ordinary pushes do not publish images.

1. Resolve repository visibility/deadline requirements with the owner, then push the reviewed changes, including the workflow, to the default branch through the team's normal review process.
2. Open **Actions → Publish tested Docker image → Run workflow**. Choose a release tag such as `1.0.0`.
3. The job runs pytest, builds the image, verifies offline samples/readiness, publishes, pulls the exact digest, and repeats offline checks. Its readiness placeholder makes no paid model call and does not establish live-model accuracy.
4. Copy the actual image reference/digest from the successful job summary. This repository's published image is `ghcr.io/myshphew/bup-cse-preliminary-round:1.0.0`; anonymous access has been verified. Its immutable digest is recorded in [registry-publication.json](registry-publication.json).
5. The package owner must configure access for judges. A public repository does not prove an image is anonymously pullable. Follow [GitHub's package visibility instructions](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility), then check with an empty Docker configuration.

Example anonymous pull after publication; replace the image reference with the successful workflow's actual digest:

```powershell
$registryCheckDirectory = Join-Path $env:TEMP ('gridwise-registry-check-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $registryCheckDirectory | Out-Null
docker --config $registryCheckDirectory pull ghcr.io/OWNER/bup-cse-preliminary-round@sha256:ACTUAL_DIGEST
```

Start that exact image with runtime credentials and run a real sample. The workflow checks an authenticated pull; anonymous access and full live-model behavior must also pass before submission.

## Deploy to the selected hosting account

The current service uses Render Free in Oregon, with `PORT=10000`, the default image command, and `/health` as its health-check path. The app binds to `0.0.0.0` and honors platform-provided `PORT`; its local default is 8000. No database or persistent volume is required. Free instances sleep after 15 idle minutes and take about a minute to wake, so cold-start availability does not meet the challenge's 30-second limit reliably. See [Render's documented limitations](https://render.com/docs/free).

Configure server-side values:

```dotenv
OPENAI_API_KEY=<set privately in the hosting secret manager>
OPENAI_MODEL=gpt-5.6-terra
OPENAI_REASONING_EFFORT=none
INTERPRETATION_CACHE_SIZE=128
```

Use the image's start command, `python run.py`, with `/health` as health path. Keep both judge endpoints accessible without login. Leave other tested limits at documented defaults unless host measurements justify changes. Never put the key in the Dockerfile, build arguments, repository, video, or public submission fields.

## Verify the public URL

Substitute the deployed base URL. The evaluator makes paid requests using the host's configured credentials:

```powershell
curl.exe https://bup-cse-preliminary-round-1-0-0.onrender.com/health
.\.venv\Scripts\python.exe -m scripts.evaluate_samples --url https://bup-cse-preliminary-round-1-0-0.onrender.com --repeat 3 --output output/public-live-benchmark.json
```

For uncached latency evidence, set hosted `INTERPRETATION_CACHE_SIZE=0` and restart/redeploy first. Restore 128 and restart afterward, then verify a final real request. Do not report warm-cache results as first-seen-note latency.

In Render, use **Environment → Edit → Save and deploy** for configuration changes. Saving without deploying does not update the running process. A successful `/health` response verifies configuration and CBC readiness, but does not validate the key with OpenAI. Always run a full official sample after changing the key. Enter credentials directly into the host's secret fields.

Record the base URL, image digest, deployed settings, release commit, verification time, pass count, p95, and maximum latency. Test from a second network, verify anonymous image access, and keep the service/quota available throughout evaluation. Local measurements do not prove hosted latency or reachability.
