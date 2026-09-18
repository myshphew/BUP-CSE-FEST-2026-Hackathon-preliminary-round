"""Evaluate the unchanged organizer sample pack offline or against a running API."""

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import httpx

from errors import ServiceError
from models import Scenario
from optimizer import optimize
from schedule_validator import TOLERANCE, validate_schedule
from validator import validate_interpretation

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "BUP_CSE_FEST_2026_Preli_Public_Sample_Cases.json"
OFFICIAL_SHA256 = "fa6abd71868e0faf429a87429d7d4a2b7bfd38c5551565637498d7fec68d5f32"


def semantics_match(actual, expected):
    if len(actual) != len(expected):
        return False
    for left, right in zip(actual, expected):
        for key in ("note_index", "applies", "directive_type"):
            if left[key] != right[key]:
                return False
        a, b = left["structured_adjustment"], right["structured_adjustment"]
        if a is None or b is None:
            if a != b: return False
            continue
        if a.keys() != b.keys() or a["hours"] != b["hours"]:
            return False
        for key in b.keys() - {"hours"}:
            if abs(a[key] - b[key]) > TOLERANCE:
                return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="Use organizer interpretations to test math only; no language model evaluation")
    mode.add_argument("--url", default="http://127.0.0.1:8000", help="Base URL for the full deployed pipeline")
    parser.add_argument("--limit", type=int, choices=range(1, 11), default=10)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--output", type=Path, help="Save machine-readable results")
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    content = SAMPLE_PATH.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if digest != OFFICIAL_SHA256:
        parser.error("Official sample checksum mismatch; restore the original file")
    cases = json.loads(content)["cases"][:args.limit]
    results = []
    print("OFFLINE: organizer interpretations supplied; LLM is NOT evaluated." if args.offline else "HTTP: exercising the running interpretation + optimization pipeline.")
    with httpx.Client(base_url=args.url.rstrip("/"), timeout=30, follow_redirects=False) as client:
        if not args.offline:
            try:
                health = client.get("/health")
                if health.status_code != 200 or health.json().get("status") != "ok":
                    print("FAIL: API not ready. Check credentials, solver, and startup logs.")
                    return 1
            except (httpx.HTTPError, ValueError):
                print("FAIL: Cannot reach a healthy API.")
                return 1
        for repetition in range(args.repeat):
            for case in cases:
                started = time.perf_counter()
                entry = {"case_id": case["id"], "repetition": repetition + 1, "passed": False}
                try:
                    scenario = Scenario.model_validate(case["input"])
                    reference = case["expected_output"]
                    truth = validate_interpretation({"directive_interpretation": reference["directive_interpretation"]}, scenario)
                    if args.offline:
                        result = optimize(scenario, truth).model_dump()
                    else:
                        response = client.post("/optimize-energy", json=case["input"])
                        response.raise_for_status()
                        result = response.json()
                    checked = validate_schedule(scenario, result, ground_truth=truth)
                    same = semantics_match(result["directive_interpretation"], reference["directive_interpretation"])
                    gap = checked.total_cost_bdt - reference["total_cost_bdt"]
                    entry.update(passed=same and abs(gap) <= TOLERANCE, interpretation_matches=same,
                                 cost_bdt=checked.total_cost_bdt, reference_cost_bdt=reference["total_cost_bdt"],
                                 cost_difference_bdt=gap)
                except ServiceError as exc:
                    entry["error"] = exc.code
                except (httpx.HTTPError, ValueError, KeyError, TypeError):
                    entry["error"] = "invalid_or_failed_response"
                entry["elapsed_seconds"] = round(time.perf_counter() - started, 6)
                results.append(entry)
                print(f"{'PASS' if entry['passed'] else 'FAIL'} {case['id']} "
                      f"{entry['elapsed_seconds']:.3f}s cost={entry.get('cost_bdt', 'unavailable')}")
    times = sorted(x["elapsed_seconds"] for x in results)
    report = {
        "mode": "offline_math_only" if args.offline else "http_full_pipeline",
        "official_sample_sha256": digest,
        "passed": sum(x["passed"] for x in results), "total": len(results),
        "p95_seconds": times[math.ceil(len(times) * 0.95) - 1],
        "max_seconds": max(times), "results": results,
    }
    print(f"{report['passed']}/{report['total']} passed; p95={report['p95_seconds']:.3f}s")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
