"""Start an isolated real API and benchmark live OpenAI over TCP without editing .env.

Uses paid model calls. The temporary server is always stopped afterward, and an
already-running development server is left alone. Cache defaults to zero.
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx

from config import load_settings

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", help="MODEL:EFFORT; defaults to the configured production profile")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--cache-size", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("output/live-http-verification.json"))
    args = parser.parse_args()
    if args.repeat < 1 or not 0 <= args.cache_size <= 4096:
        parser.error("Invalid repetition or cache size")
    settings = load_settings()
    if not settings.api_key:
        raise SystemExit("No OpenAI key configured")
    model, effort = args.candidate.rsplit(":", 1) if args.candidate else (settings.model, settings.reasoning_effort)
    args.output = args.output.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pending_report = args.output.with_name(f".{args.output.stem}-{uuid.uuid4().hex}.json")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    # load_settings has loaded .env into this environment; only non-secret
    # overrides are changed here. No credential is printed or put in argv.
    env = dict(os.environ, OPENAI_MODEL=model, OPENAI_REASONING_EFFORT=effort,
               INTERPRETATION_CACHE_SIZE=str(args.cache_size))
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    command = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1",
               "--port", str(port), "--no-access-log"]
    with args.output.with_suffix(".server.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log, creationflags=flags)
        try:
            with httpx.Client(base_url=base, timeout=3) as client:
                deadline = time.monotonic() + 15
                while True:
                    try:
                        health = client.get("/health")
                        if health.status_code != 200:
                            raise RuntimeError("Temporary server is not ready")
                        break
                    except httpx.ConnectError:
                        if process.poll() is not None or time.monotonic() > deadline:
                            raise RuntimeError("Temporary server failed to start")
                        time.sleep(0.1)
            print(f"LIVE HTTP profile: {model}/{effort}; cache={args.cache_size}", flush=True)
            completed = subprocess.run([
                sys.executable, "-m", "scripts.evaluate_samples", "--url", base,
                "--repeat", str(args.repeat), "--output", str(pending_report),
            ], cwd=ROOT, env=env)
            if pending_report.exists():
                report = json.loads(pending_report.read_text(encoding="utf-8"))
                report.update(model=model, reasoning_effort=effort,
                              application_cache_size=args.cache_size, live_llm_evaluated=True)
                pending_report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
                pending_report.replace(args.output)
            return completed.returncode
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            pending_report.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
