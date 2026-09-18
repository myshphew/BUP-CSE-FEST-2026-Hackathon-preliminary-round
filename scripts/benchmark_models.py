"""Live model comparison through the production API, with application caching off.

Uses paid OpenAI calls. No local server restart or .env change is needed.
Official cases or explicitly labeled wording-only variants are used. Candidates run sequentially in a
rotating order to reduce order bias, using a shared client for each candidate.
"""

import argparse
import asyncio
import hashlib
import json
import math
import statistics
import sys
import time
from contextlib import AsyncExitStack
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import httpx

from config import load_settings
from main import create_app
from models import Scenario
from schedule_validator import TOLERANCE, validate_schedule
from scripts.evaluate_samples import OFFICIAL_SHA256, SAMPLE_PATH, semantics_match
from validator import validate_interpretation


def summarize(results):
    times = sorted(r["elapsed_seconds"] for r in results)
    return {"passed": sum(r["passed"] for r in results), "total": len(results),
            "p50_seconds": statistics.median(times),
            "p95_seconds": times[math.ceil(0.95 * len(times)) - 1],
            "max_seconds": max(times), "results": results}


async def benchmark(args):
    settings = load_settings()
    if not settings.api_key:
        raise SystemExit("No OpenAI key configured; set it locally without printing it.")
    content = SAMPLE_PATH.read_bytes()
    if hashlib.sha256(content).hexdigest() != OFFICIAL_SHA256:
        raise SystemExit("Official sample checksum mismatch")
    cases = json.loads(content)["cases"][:args.limit]
    if args.language_checks:
        from scripts.language_checks import make_language_checks
        cases = make_language_checks(json.loads(content)["cases"])
    if args.stress_language_checks:
        from scripts.language_checks import make_stress_language_checks
        cases = make_stress_language_checks(json.loads(content)["cases"])
    candidates = args.candidate or ["gpt-6-astra:low", "gpt-5.6-sol:none", "gpt-5.6-terra:none"]
    if len(set(candidates)) != len(candidates):
        raise SystemExit("Candidate names must be unique")
    report = {"mode": "live_openai_through_in_process_production_api", "application_cache_size": 0,
              "dataset": ("stress_language_checks" if args.stress_language_checks else
                          "supplemental_language_checks" if args.language_checks else "official_samples"),
              "started_at": datetime.now(timezone.utc).isoformat(), "official_sample_sha256": OFFICIAL_SHA256,
              "candidates": {name: {"results": []} for name in candidates}}

    def save():
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    async with AsyncExitStack() as stack:
        clients = {}
        for name in candidates:
            model, effort = name.rsplit(":", 1)
            config = replace(settings, model=model, reasoning_effort=effort, cache_size=0)
            app = create_app(config)
            await stack.enter_async_context(app.router.lifespan_context(app))
            client = await stack.enter_async_context(httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://benchmark", timeout=30))
            if (await client.get("/health")).status_code != 200:
                raise SystemExit("Benchmark app is not ready")
            clients[name] = client
        for repetition in range(args.repeat):
            for case_number, case in enumerate(cases):
                offset = (repetition + case_number) % len(candidates)
                ordered = candidates[offset:] + candidates[:offset]
                for name in ordered:
                    started = time.perf_counter()
                    entry = {"case_id": case["id"], "repetition": repetition + 1, "passed": False}
                    response = await clients[name].post("/optimize-energy", json=case["input"])
                    # Stop the timer before evaluator work, matching server response latency.
                    entry["elapsed_seconds"] = round(time.perf_counter() - started, 6)
                    entry["http_status"] = response.status_code
                    if response.status_code == 200:
                        try:
                            scenario = Scenario.model_validate(case["input"])
                            truth = validate_interpretation({"directive_interpretation": case["expected_output"]["directive_interpretation"]}, scenario)
                            data = response.json()
                            result = validate_schedule(scenario, data, ground_truth=truth)
                            same = semantics_match(data["directive_interpretation"], case["expected_output"]["directive_interpretation"])
                            gap = result.total_cost_bdt - case["expected_output"]["total_cost_bdt"]
                            entry.update(passed=same and abs(gap) <= TOLERANCE,
                                         interpretation_matches=same, cost_difference_bdt=gap)
                            if not same:
                                entry["actual_interpretation"] = data["directive_interpretation"]
                        except Exception:
                            entry["error"] = "evaluation_failed"
                    else:
                        entry["error"] = "request_failed"
                    results = report["candidates"][name]["results"]
                    results.append(entry)
                    report["candidates"][name] = summarize(results)
                    save()
                    print(f"{'PASS' if entry['passed'] else 'FAIL'} {name} {case['id']} {entry['elapsed_seconds']:.3f}s", flush=True)
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    save()
    for name, result in report["candidates"].items():
        print(f"{name}: {result['passed']}/{result['total']} passed; p95={result['p95_seconds']:.3f}s", flush=True)
    return 0 if all(r["passed"] == r["total"] for r in report["candidates"].values()) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", help="MODEL:EFFORT; repeat for each candidate")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--limit", type=int, choices=range(1, 11), default=10)
    language = parser.add_mutually_exclusive_group()
    language.add_argument("--language-checks", action="store_true", help="Use explicitly labeled paraphrase/injection variants; official JSON remains unchanged")
    language.add_argument("--stress-language-checks", action="store_true", help="Audit wording contrasts, equivalent numbers, listed hours, distractors, and note-order changes")
    parser.add_argument("--output", type=Path, default=Path("output/model-comparison.json"))
    args = parser.parse_args()
    if args.repeat < 1: parser.error("--repeat must be positive")
    return asyncio.run(benchmark(args))


if __name__ == "__main__":
    sys.exit(main())
