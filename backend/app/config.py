"""Settings for the OpsIQ backend.

Every setting is read from an environment variable, with a default that
works for local development. Nothing here is secret.

| Variable             | Default                                         |
|----------------------|-------------------------------------------------|
| OPSIQ_ENV            | development                                     |
| OPSIQ_DATA_DIR       | data/raw (inside the project)                   |
| OPSIQ_CORS_ORIGINS   | http://localhost:5173,http://127.0.0.1:5173     |
| OPSIQ_LOG_LEVEL      | INFO                                            |
| OPSIQ_PRELOAD_DATA   | true                                            |

OPSIQ_CORS_ORIGINS is a comma-separated list of the web addresses
(origins) allowed to call the API from a browser.

OPSIQ_PRELOAD_DATA=true calculates all analytics in the background as
soon as the server starts, so the first dashboard visit is fast.
"""

import os
from dataclasses import dataclass
from pathlib import Path

# The project root is three folders above this file
# (config.py -> app -> backend -> OpsIQ).
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


@dataclass(frozen=True)
class Settings:
    environment: str
    data_dir: Path
    cors_origins: list[str]
    log_level: str
    preload_data: bool


def _parse_origins(value):
    """Split a comma-separated list of origins, ignoring blanks.

    A trailing slash is removed because browsers send the origin
    without one, for example "https://example.com".
    """

    return [
        origin.strip().rstrip("/")
        for origin in value.split(",")
        if origin.strip()
    ]


def _resolve_data_dir(value):
    """Return the data folder; relative paths start at the project root."""

    path = Path(value)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    return path


def load_settings(environ=None):
    """Build the settings from environment variables.

    Args:
        environ: A mapping of variable names to values. Defaults to the
            real environment. Tests pass a plain dictionary instead.
    """

    environ = os.environ if environ is None else environ

    return Settings(
        environment=environ.get("OPSIQ_ENV", "development"),
        data_dir=_resolve_data_dir(
            environ.get("OPSIQ_DATA_DIR", "data/raw")
        ),
        cors_origins=_parse_origins(
            environ.get("OPSIQ_CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
        ),
        log_level=environ.get("OPSIQ_LOG_LEVEL", "INFO").upper(),
        preload_data=(
            environ.get("OPSIQ_PRELOAD_DATA", "true").strip().lower()
            in {"1", "true", "yes", "on"}
        ),
    )


settings = load_settings()
