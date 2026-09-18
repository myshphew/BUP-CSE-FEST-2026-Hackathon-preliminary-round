"""Environment configuration; credentials are never included in repr/log output."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str = field(default="", repr=False)
    model: str = "gpt-6-astra"
    reasoning_effort: str = "low"
    openai_timeout: float = 20.0
    max_output_tokens: int = 2048
    request_timeout: float = 28.0
    solver_timeout: float = 3.0
    max_concurrent_requests: int = 8
    cache_size: int = 128

    def __post_init__(self):
        if not (
            self.model.strip()
            and self.reasoning_effort in {"none", "low", "medium", "high", "xhigh", "max"}
            and not (self.model.startswith("gpt-6-astra") and self.reasoning_effort == "none")
            and 0 < self.openai_timeout < self.request_timeout < 30
            and 0 < self.solver_timeout < self.request_timeout
            and 256 <= self.max_output_tokens <= 16384
            and 1 <= self.max_concurrent_requests <= 64
            and 0 <= self.cache_size <= 4096
        ):
            raise ValueError("Invalid service configuration")


def load_settings() -> Settings:
    load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
    try:
        return Settings(
            api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            model=os.getenv("OPENAI_MODEL", "gpt-6-astra"),
            reasoning_effort=os.getenv("OPENAI_REASONING_EFFORT", "low"),
            openai_timeout=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20")),
            max_output_tokens=int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "2048")),
            request_timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "28")),
            solver_timeout=float(os.getenv("SOLVER_TIMEOUT_SECONDS", "3")),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "8")),
            cache_size=int(os.getenv("INTERPRETATION_CACHE_SIZE", "128")),
        )
    except (ValueError, TypeError):
        raise RuntimeError("Invalid service configuration; check documented environment variables.") from None
