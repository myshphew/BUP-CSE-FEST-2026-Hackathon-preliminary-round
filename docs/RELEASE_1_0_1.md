# Verified 1.0.1 candidate and promotion instructions

The candidate is implemented, tested and published. The local Compose service runs it with Terra/low and cache 128. The public Render service remains 1.0.0/Terra-none pending clarification of the competition deadline and update policy. These instructions are a prepared promotion path, not a claim that 1.0.1 is already hosted.

## Exact image

Tag: `ghcr.io/myshphew/bup-cse-preliminary-round:1.0.1`

Immutable reference: `ghcr.io/myshphew/bup-cse-preliminary-round@sha256:ba5d3121fa96f19d50fd698494fa50de4de8344da5ac4c64aa8558ad8f264c4a`

Source commit: `54a8b1d5edda0504c74f62b21305d5b1173c9227`. [Publication workflow](https://github.com/myshphew/BUP-CSE-FEST-2026-Hackathon-preliminary-round/actions/runs/35372128259) passed. An empty Docker configuration pulled the image anonymously, all ten offline official costs passed, and a real OpenAI request from the pulled image returned the correct cost and improved peak.

## Run without changing the current competition service

Place the existing OpenAI key in a private local `.env` under `OPENAI_API_KEY`; never put it in source or an image. These commands use host port 8001 to avoid the existing Compose service:

```bash
docker pull ghcr.io/myshphew/bup-cse-preliminary-round@sha256:ba5d3121fa96f19d50fd698494fa50de4de8344da5ac4c64aa8558ad8f264c4a
docker run --rm --name gridwise-candidate -p 8001:8000 --env-file .env -e OPENAI_MODEL=gpt-5.6-terra -e OPENAI_REASONING_EFFORT=low -e INTERPRETATION_CACHE_SIZE=128 -e PORT=8000 ghcr.io/myshphew/bup-cse-preliminary-round@sha256:ba5d3121fa96f19d50fd698494fa50de4de8344da5ac4c64aa8558ad8f264c4a
```

In another terminal, use `curl.exe` on Windows:

```bash
curl http://127.0.0.1:8001/health
docker exec gridwise-candidate python -m scripts.evaluate_samples --url http://127.0.0.1:8000 --limit 1
```

SAMPLE-01 cost remains **38,365 BDT**, and peak grid is **175 kWh**. Run all cases by omitting `--limit 1`. To reproduce an uncached benchmark, restart with cache 0, run `--repeat 3`, then restore 128. These commands make real model calls.

## Prepared Render promotion

After establishing that the organizer allows the update:

1. Set the existing Render service's image source to the immutable 1.0.1 reference above. Keep the Free plan, existing service URL, default image command, port 10000 and `/health` path.
2. Keep the existing secret; set `OPENAI_MODEL=gpt-5.6-terra`, `OPENAI_REASONING_EFFORT=low`, and cache 0. Save and deploy.
3. Wait for Live, verify `/health`, then run the official HTTP evaluator three times against the public URL. Verify OpenAPI reports 1.0.1 and SAMPLE-01 has cost 38,365 / peak 175.
4. Restore cache 128, save/deploy, and verify one fresh request plus a cached repeat.
5. Record the actual hosted p95 and image digest in the submission manifest. Do not copy local-container latency into a hosted report.

The previous published 1.0.0 image remains available for rollback. Render Free idle suspension is unchanged by this release.

## Candidate artifacts

`output/submission/1.0.1/` contains the updated 2:38 video, source archive, full benchmark reports, audit report, checksums and manifest. See [JUDGE_AUDIT.md](JUDGE_AUDIT.md) for every rubric criterion and [audit-verification.json](audit-verification.json) for machine-readable results.
