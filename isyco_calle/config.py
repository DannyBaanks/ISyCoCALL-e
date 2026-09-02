"""Secure configuration.

Secrets come exclusively from environment variables. No tokens are hardcoded.
The env var name follows the official CALL-E SDK: CALLE_API_KEY.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

# Official env var names (verified against call-e-integrations README / SDK).
ENV_API_KEY = "CALLE_API_KEY"
ENV_BASE_URL = "CALLE_BASE_URL"
ENV_TIMEOUT = "CALLE_TIMEOUT"
ENV_CALLER = "ISYCO_CALL_DEFAULT_CALLER"

DEFAULT_BASE_URL = "https://api.heycall-e.com"
DEFAULT_TIMEOUT = 120.0


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    calle_api_key: str
    calle_base_url: str = DEFAULT_BASE_URL
    calle_timeout: float = DEFAULT_TIMEOUT
    default_caller: Optional[str] = None

    def validate(self) -> "Settings":
        if not self.calle_api_key or not self.calle_api_key.strip():
            raise ConfigError(
                f"{ENV_API_KEY} is not set. Get an API key from the CALL-E dashboard "
                "(https://dashboard.heycall-e.com/account/api-keys) and export it."
            )
        if self.calle_api_key.strip().lower() in {"your_api_key", "calle_live_key", "x", ""}:
            raise ConfigError(f"{ENV_API_KEY} looks like a placeholder, not a real key.")
        return self

    @classmethod
    def load(cls, env: Optional[dict] = None) -> "Settings":
        env = os.environ if env is None else env
        key = env.get(ENV_API_KEY, "")
        try:
            timeout = float(env.get(ENV_TIMEOUT, str(DEFAULT_TIMEOUT)))
        except ValueError:
            timeout = DEFAULT_TIMEOUT
        return cls(
            calle_api_key=key.strip(),
            calle_base_url=env.get(ENV_BASE_URL, DEFAULT_BASE_URL).strip(),
            calle_timeout=timeout,
            default_caller=env.get(ENV_CALLER) or None,
        )