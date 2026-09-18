import asyncio
import copy
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from config import Settings
from errors import ProviderError
from main import create_app
from models import Scenario
from schedule_validator import validate_schedule
from conftest import CASES


class FixtureInterpreter:
    """Official expectations injected in tests only; not language evaluation."""
    ready = True

    def __init__(self, raw=None):
        self.raw = raw
        self.calls = 0

    async def interpret(self, scenario):
        self.calls += 1
        if self.raw is not None:
            return self.raw
        for case in CASES:
            if case["input"]["operator_notes"] == scenario.operator_notes:
                return {"directive_interpretation": copy.deepcopy(case["expected_output"]["directive_interpretation"])}
        raise RuntimeError("No official test fixture")


@pytest.fixture
def client():
    with TestClient(create_app(Settings(), FixtureInterpreter())) as result:
        yield result


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_official_api_pipeline(client, case):
    response = client.post("/optimize-energy", json=case["input"])
    assert response.status_code == 200
    result = validate_schedule(Scenario.model_validate(case["input"]), response.json())
    assert abs(result.total_cost_bdt - case["expected_output"]["total_cost_bdt"]) <= 0.01


@pytest.mark.parametrize("body", ["{", "null", "[]", "{}", '{"secret":"DO_NOT_ECHO"}'])
def test_malformed_input_returns_400(client, body):
    response = client.post("/optimize-energy", content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    assert "DO_NOT_ECHO" not in response.text
    assert response.json()["error"]["code"] == "invalid_request"


def test_semantically_invalid_request_returns_400(client, case):
    case["input"]["hours"][0]["hour"] = 24
    assert client.post("/optimize-energy", json=case["input"]).status_code == 400


def test_missing_key_does_not_claim_readiness_or_return_no_op(case):
    with TestClient(create_app(Settings(api_key=""))) as client:
        assert client.get("/health").status_code == 500
        response = client.post("/optimize-energy", json=case["input"])
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "service_not_ready"


def test_missing_solver_does_not_claim_readiness(monkeypatch):
    monkeypatch.setattr("main.solver_ready", lambda: False)
    with TestClient(create_app(Settings(), FixtureInterpreter())) as client:
        assert client.get("/health").status_code == 500


@pytest.mark.parametrize("mode", ["provider", "unexpected", "invalid"])
def test_model_failures_are_safe_and_do_not_run_solver(case, mode, monkeypatch, caplog):
    class BrokenInterpreter(FixtureInterpreter):
        async def interpret(self, scenario):
            if mode == "provider": raise ProviderError("DO_NOT_ECHO")
            if mode == "unexpected": raise RuntimeError("DO_NOT_ECHO")
            return {"directive_interpretation": [], "secret": "DO_NOT_ECHO"}
    def forbidden(*args):
        pytest.fail("Unvalidated output reached the optimizer")
    monkeypatch.setattr("main.optimize", forbidden)
    with TestClient(create_app(Settings(), BrokenInterpreter())) as client:
        response = client.post("/optimize-energy", json=case["input"])
    assert response.status_code == 500
    assert "DO_NOT_ECHO" not in response.text + caplog.text
    assert "Traceback" not in caplog.text


def test_request_deadline(case):
    class SlowInterpreter(FixtureInterpreter):
        async def interpret(self, scenario):
            await asyncio.sleep(1)
    settings = Settings(request_timeout=0.04, openai_timeout=0.01, solver_timeout=0.01)
    with TestClient(create_app(settings, SlowInterpreter())) as client:
        response = client.post("/optimize-energy", json=case["input"])
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "request_timeout"


def test_infeasible_request_is_controlled(case):
    case["input"]["operator_notes"] = ["Unit-test impossible grid cap"]
    raw = {"directive_interpretation": [{"note_index": 0, "applies": True,
        "directive_type": "max_grid_window", "structured_adjustment": {"hours": [0], "max_grid_kwh": 0},
        "explanation": "Unit constraint"}]}
    with TestClient(create_app(Settings(), FixtureInterpreter(raw))) as client:
        response = client.post("/optimize-energy", json=case["input"])
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "infeasible_constraints"


def test_nonfinite_json_is_safely_rejected(client, case):
    body = json.dumps(case["input"]).replace('"demand_kwh": 90', '"demand_kwh": NaN', 1)
    assert client.post("/optimize-energy", content=body, headers={"Content-Type": "application/json"}).status_code == 400


def test_unordered_hours_still_return_sorted_plan(client, case):
    case["input"]["hours"].reverse()
    response = client.post("/optimize-energy", json=case["input"])
    assert response.status_code == 200
    assert [h["hour"] for h in response.json()["hourly_plan"]] == list(range(24))


def test_concurrent_requests_remain_isolated():
    async def run():
        app = create_app(Settings(max_concurrent_requests=3), FixtureInterpreter())
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                responses = await asyncio.gather(*[client.post("/optimize-energy", json=c["input"]) for c in CASES])
                for case, response in zip(CASES, responses):
                    assert response.status_code == 200
                    result = validate_schedule(Scenario.model_validate(case["input"]), response.json())
                    assert result.scenario_id == case["input"]["scenario_id"]
    asyncio.run(run())
