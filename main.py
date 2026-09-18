"""FastAPI orchestration: interpret -> validate -> optimize -> independently replay."""

import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from config import Settings, load_settings
from errors import DeadlineError, NotReadyError, ServiceError
from interpreter import Interpreter, OpenAIInterpreter
from models import OptimizationResponse, Scenario
from optimizer import optimize, solver_ready
from schedule_validator import validate_schedule
from validator import validate_interpretation

logger = logging.getLogger("gridwise")


def create_app(settings: Settings | None = None, interpreter: Interpreter | None = None) -> FastAPI:
    # The optional object is dependency injection for tests, never a public API or
    # environment-controlled shortcut around the required production LLM.
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        config = settings if settings is not None else load_settings()
        active_interpreter = interpreter if interpreter is not None else OpenAIInterpreter(config)
        app.state.config = config
        app.state.interpreter = active_interpreter
        app.state.solver_ready = await asyncio.to_thread(solver_ready)
        app.state.slots = asyncio.Semaphore(config.max_concurrent_requests)
        try:
            yield
        finally:
            if isinstance(active_interpreter, OpenAIInterpreter):
                await active_interpreter.close()

    application = FastAPI(title="GridWise Campus Energy Optimizer", version="1.0.0", lifespan=lifespan)

    @application.middleware("http")
    async def contain_unexpected_errors(request: Request, call_next):
        # Catch before Starlette's ServerErrorMiddleware re-raises to Uvicorn,
        # which would otherwise log an exception traceback after sending JSON.
        try:
            return await call_next(request)
        except Exception:
            logger.error("request_failed code=internal_error")
            return JSONResponse(status_code=500, content={"error": {
                "code": ServiceError.code, "message": ServiceError.message,
            }})

    @application.exception_handler(RequestValidationError)
    async def bad_request(request: Request, exc: RequestValidationError):
        # Pydantic errors contain the offending input. Never echo/log it.
        return JSONResponse(status_code=400, content={"error": {
            "code": "invalid_request", "message": "Request JSON does not match the required scenario schema.",
        }})

    @application.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        logger.warning("request_failed code=%s", exc.code)
        return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}})

    @application.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        # No exception text, input, provider payload, or traceback is logged.
        logger.error("request_failed code=internal_error")
        return JSONResponse(status_code=500, content={"error": {
            "code": ServiceError.code, "message": ServiceError.message,
        }})

    def ensure_ready():
        if not application.state.solver_ready or not application.state.interpreter.ready:
            raise NotReadyError()

    @application.get("/health")
    async def health():
        ensure_ready()
        return {"status": "ok"}

    @application.post("/optimize-energy", response_model=OptimizationResponse)
    async def optimize_energy(scenario: Scenario):
        ensure_ready()
        started = time.perf_counter()
        config = application.state.config
        try:
            # Queue wait is included in the overall deadline.
            async with asyncio.timeout(config.request_timeout):
                async with application.state.slots:
                    raw = await application.state.interpreter.interpret(scenario)
                    directives = validate_interpretation(raw, scenario)
                    result = await asyncio.to_thread(optimize, scenario, directives, config.solver_timeout)
                    result = validate_schedule(scenario, result)
        except TimeoutError as exc:
            raise DeadlineError() from exc
        logger.info("optimization_completed elapsed_ms=%.1f", (time.perf_counter() - started) * 1000)
        return result

    return application


app = create_app()
