# Current submission status and next actions

Verified on 2026-09-18. The public API is live on Render Free. All **30/30 official requests passed with application cache disabled: p95 2.641738 seconds, maximum 3.379812 seconds**. The original sample JSON is unchanged. The hosted key was corrected by the user and loaded through a new deployment. Normal caching is restored to 128.

## Submission references

| Item | Reference |
|---|---|
| Public API base URL | https://bup-cse-preliminary-round-1-0-0.onrender.com |
| Health endpoint | https://bup-cse-preliminary-round-1-0-0.onrender.com/health |
| Optimization endpoint | `POST https://bup-cse-preliminary-round-1-0-0.onrender.com/optimize-energy` |
| API documentation | https://bup-cse-preliminary-round-1-0-0.onrender.com/docs |
| Repository | https://github.com/myshphew/BUP-CSE-FEST-2026-Hackathon-preliminary-round |
| Public image tag | `ghcr.io/myshphew/bup-cse-preliminary-round:1.0.0` |
| Immutable image | `ghcr.io/myshphew/bup-cse-preliminary-round@sha256:262f30a45145c18310a61c34d4f7483b81dd7bb7293d81045938707c06b1d20f` |
| Video | `output/submission/gridwise-solution.mp4`, 2:44, also uploaded to the private draft release |
| Hosted evidence | [public-verification.json](public-verification.json), [all 30 requests](public-live-benchmark.json) |

The public image's source commit is `60ec64fb7c1dc70a462cca795d4c71e712e981f0`. Later diagnostic logging and delivery-documentation changes do not change that deployed image. The source archive and pull request identify the newer source separately.

## Completed

- Implementation, independent replay, official sample evaluation, Linux Docker checks, and model comparisons.
- 165 tests for the deployed image; 168 tests after additional safe provider diagnostic logging, with successful CI.
- Anonymous pull of the exact published image; 10/10 offline cases and a real OpenAI request from that image.
- Free Render deployment in Oregon, port 10000, default image command, `/health` health path.
- Public uncached benchmark through real OpenAI; normal cache restored to 128 and final checks recorded in the hosted evidence.
- Narrated video, source archive, checksums, submission manifest, and private draft release assets.

## What the team must do next

1. **Confirm repository visibility with the owner.** GitHub reports the repository is private. The guide requires it private during the event and public after the deadline. You supplied 10 PM Bangladesh time, but no date; verify the actual organizer deadline. The connected collaborator has push permission, not repository administration permission.
2. **Make the video accessible to judges.** Upload the prepared MP4 directly to the organizer, or have the owner publish the [prepared draft release](https://github.com/myshphew/BUP-CSE-FEST-2026-Hackathon-preliminary-round/releases/tag/untagged-0fe99429f0f23eb64103) when permitted. A draft release/private repository is not publicly accessible.
3. **Submit the references above through the organizer's official form.** The form/link has not been provided, so no final submission has been made. Include the immutable image reference as the fallback. Never include `.env` or the API key.
4. **Before judging, check the health endpoint and one official optimization request from another network**, such as mobile data. Review the video and architecture so the team can explain the LLM boundary, deterministic solver, and independent replay. Keep the existing OpenAI key valid with model access and available quota.

## Hosting limitation

[Render Free](https://render.com/docs/free) suspends the instance after 15 minutes without traffic and can take about a minute to wake. The passing benchmark measures a running instance, not wake-up after idle. Cache 128 speeds repeated interpretations but cannot remove this host cold-start limit. Continuous availability and every cold request below 30 seconds are therefore not guaranteed. The pullable Docker image is the tested fallback. No paid hosting plan was enabled.

The optional [Render Blueprint](../deploy/render-free.yaml) creates an independent service if explicitly applied; it does not manage the existing service automatically. It starts with cache zero for measurement. The current deployed service has cache 128. OpenAI API usage still consumes the existing account's quota.

## New audited candidate

Version 1.0.1 is implemented, published, anonymously pullable and running locally with Terra/low. It preserves official minimum bills, lowers peaks on two official cases, and adds bounded transient retries. It passed 243 tests and 30/30 uncached Docker HTTP requests, p95 2.673 s. It is kept separate from the public competition service while deadline/update eligibility is clarified. See [the complete judge audit](JUDGE_AUDIT.md) and [candidate promotion instructions](RELEASE_1_0_1.md). The updated candidate video is 2:38 and is in `output/submission/1.0.1/`.
