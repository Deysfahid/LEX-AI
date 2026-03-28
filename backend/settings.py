import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _parse_origins(value: str | None) -> List[str]:
    if not value:
        return []
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    env_profile: str
    log_level: str
    allowed_origins: List[str]
    request_max_body_bytes: int
    readiness_require_groq: bool
    host: str
    port: int
    workers: int



def load_settings() -> Settings:
    env_profile = os.getenv("ENV_PROFILE", "development").strip().lower()
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    allowed_origins = _parse_origins(os.getenv("ALLOWED_ORIGINS"))
    if not allowed_origins and env_profile != "production":
        allowed_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    if env_profile == "production" and not allowed_origins:
        raise RuntimeError("ALLOWED_ORIGINS must be set in production.")

    request_max_body_mb = _parse_int(os.getenv("REQUEST_MAX_BODY_MB"), 12)
    readiness_require_groq = _parse_bool(os.getenv("READINESS_REQUIRE_GROQ"), False)

    host = os.getenv("HOST", "0.0.0.0")
    port = _parse_int(os.getenv("PORT"), 8000)
    workers = max(1, _parse_int(os.getenv("UVICORN_WORKERS"), 1))

    return Settings(
        env_profile=env_profile,
        log_level=log_level,
        allowed_origins=allowed_origins,
        request_max_body_bytes=request_max_body_mb * 1024 * 1024,
        readiness_require_groq=readiness_require_groq,
        host=host,
        port=port,
        workers=workers,
    )
