# Free hosting: practical options and limits

These are suggestions, not newly configured services. The current API remains on Render Free. Documentation checked on 18 September 2026; provider plans can change.

## Recommended immediate option: external health monitoring

Keep the existing URL and add an **HTTP(S) monitor every five minutes** using UptimeRobot's Free plan. Its documented free interval is five minutes. [Official plan](https://uptimerobot.com/pricing/).

Suggested setup:

1. Create a free UptimeRobot account and verify the account if requested. No paid upgrade is needed for five-minute monitoring.
2. Create an HTTP(S) monitor named `GridWise API health`.
3. Set the URL to `https://bup-cse-preliminary-round-1-0-0.onrender.com/health`.
4. Select the five-minute interval and HTTP GET. A healthy check must receive HTTP 200; verify the response is `{"status":"ok"}`.
5. Enable the available outage notification to the account owner. Check that repeated monitoring requests actually reach the service.
6. Before the evaluation window, verify a real official optimization request as well. `/health` does not check OpenAI quota, model access or semantic correctness.

Do not supply an OpenAI key to the monitor. Do not repeatedly call `/optimize-energy` just to keep the service awake: `/health` makes no model call. No monitor or scheduled keep-alive was created as part of this documentation task.

**Why this can help:** Render documents suspension after 15 minutes without inbound requests. A successful five-minute external check should usually prevent that idle condition. This is an inference from the documented traffic rule, not a Render availability guarantee. A self-ping inside a suspended container cannot wake that container. [Render Free documentation](https://render.com/docs/free).

Monitoring does not remove cold starts after restarts, platform outages, missed checks or resource limits. Render can restart free services; 750 running-instance hours are shared across the workspace per month. Multiple services share that allowance. Track remaining hours and bandwidth in the dashboard. Keeping a process awake consumes its allowance. Warm-request p95 does not prove uninterrupted availability or compliance with the 30-second judge timeout.

## Backup without a new hosting bill: existing computer plus a tunnel

An already-running Docker service can be exposed through Cloudflare's free **Quick Tunnel** for a temporary backup or supervised demonstration. With `cloudflared` installed, a local service on port 8000 can be exposed using:

```bash
cloudflared tunnel --url http://localhost:8000
```

The tunnel prints a public HTTPS URL. Verify `/health` and a real sample from another network. Keep Docker, the tunnel, the computer, power and internet running; disable computer sleep during the session. Only use this as a competition endpoint if organizer rules allow it and the URL will remain available throughout evaluation.

Quick Tunnels use a random hostname, have no uptime SLA, are intended for testing/development and have a 200 in-flight request limit. Restarting the tunnel may change the URL. A laptop/tunnel is therefore a **backup**, not a stronger guarantee than hosted service. These limitations come from [Cloudflare's documentation](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/).

## Better continuous availability if already available: university infrastructure

Ask the organizer or university whether a supervised always-on machine/VM and public HTTPS endpoint can be provided without charge to the team. Run the same verified Docker image, supply the key as a runtime secret, and validate it externally. This depends on institutional access; it is not a claim that such hosting is available. An existing machine with a stable public endpoint avoids a free platform's idle-suspension policy, but still needs reliable power/network and maintenance.

## Why not promise another free cloud will fix everything?

- Cloud Run has a free allowance, but minimum instances incur idle billing and usage beyond allowances can be charged. It is not a guaranteed zero-cost, always-on substitute. [Official pricing](https://cloud.google.com/run/pricing).
- Hugging Face currently documents CPU Basic as having no hourly charge, **but creating a new compute Space (Docker/Gradio) requires a paid plan**. It is unsuitable as a guaranteed free new deployment under this budget. [Official Spaces overview](https://huggingface.co/docs/hub/spaces-overview).
- Moving providers introduces another deployment and re-verification step; an untested alternative does not improve the submission's evidence.

## Required fallback remains the published Docker image

Submit the exact anonymously pullable image and run command from the [README](../README.md#docker-and-deployment), with credentials through the organizer-approved private channel. The rubric explicitly checks this fallback. It does not guarantee that every live-endpoint or latency mark survives an outage, so retain honest availability limitations.

**Suggested choice:** retain Render, use free external health monitoring to reduce idle gaps, keep the verified Docker fallback accessible, and seek university hosting only if it is readily available. No paid upgrade, provider migration or tunnel has been performed.
