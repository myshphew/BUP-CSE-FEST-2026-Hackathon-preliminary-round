"""Start real Uvicorn processes and verify sockets; model output is explicitly mocked."""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    sample = json.loads((ROOT / "BUP_CSE_FEST_2026_Preli_Public_Sample_Cases.json").read_text(encoding="utf-8"))["cases"][0]["input"]
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    for mode in ("production_missing_key", "fixture_http"):
        port = free_port()
        base = f"http://127.0.0.1:{port}"
        module = "main:app" if mode == "production_missing_key" else "http_fixture_app:app"
        command = [sys.executable, "-m", "uvicorn", module, "--host", "127.0.0.1", "--port", str(port), "--no-access-log"]
        if mode == "fixture_http": command += ["--app-dir", "tests"]
        env = dict(os.environ, OPENAI_API_KEY="")
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        with (output / f"{mode}.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log, creationflags=flags)
            try:
                with httpx.Client(base_url=base, timeout=5) as client:
                    deadline = time.monotonic() + 15
                    while True:
                        try:
                            health = client.get("/health")
                            break
                        except httpx.ConnectError:
                            if process.poll() is not None or time.monotonic() > deadline:
                                raise RuntimeError("Test server did not start")
                            time.sleep(0.1)
                    if mode == "production_missing_key":
                        assert health.status_code == 500
                        assert client.post("/optimize-energy", json=sample).status_code == 500
                        print("PASS production server: missing credentials fail safely over HTTP")
                    else:
                        assert health.status_code == 200 and health.json() == {"status": "ok"}
                        print("PASS fixture server: GET /health returned HTTP 200", flush=True)
                        print("TEST ONLY: official interpretations injected; live OpenAI is NOT evaluated.", flush=True)
                        subprocess.run([sys.executable, "-m", "scripts.evaluate_samples", "--url", base,
                                        "--repeat", "3", "--output", str(output / "fixture-http-samples.json")], cwd=ROOT, check=True)
                        report_path = output / "fixture-http-samples.json"
                        report = json.loads(report_path.read_text(encoding="utf-8"))
                        report["mode"] = "http_with_official_interpretation_fixture"
                        report["live_llm_evaluated"] = False
                        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
                    malformed = client.post("/optimize-energy", content="{", headers={"Content-Type": "application/json"})
                    assert malformed.status_code == 400
                    print("PASS malformed JSON: HTTP 400")
            finally:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == "__main__":
    main()
