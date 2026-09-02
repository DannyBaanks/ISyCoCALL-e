"""In-memory mock provider, ONLY for unit tests.

Explicitly a mock: it never touches the network and never places a call. It
exists so contract/result/authority logic can be tested deterministically.
Live integration lives in providers/callee.py and is verified separately.
"""

from __future__ import annotations

import uuid
from typing import Dict, Optional

from ..domain.contract import PhoneCallRequest
from ..domain.result import PhoneCallResult, PhoneCallStatus
from .callee import TranscriptExtractor


class MockProvider:
    """Deterministic fake for tests. Set `result` to control the outcome."""

    def __init__(self) -> None:
        self.requests: list[PhoneCallRequest] = []
        self.result: Optional[PhoneCallResult] = None
        self.raise_error: Optional[Exception] = None

    def place_and_wait(self, request: PhoneCallRequest) -> PhoneCallResult:
        if self.raise_error is not None:
            raise self.raise_error
        self.requests.append(request)
        if self.result is None:
            return PhoneCallResult(
                status=PhoneCallStatus.SUCCESS,
                request_id=f"mock_{uuid.uuid4().hex[:8]}",
                provider="mock",
                structured_output={"ok": True},
            )
        return self.result

    def get(self, call_id: str) -> PhoneCallResult:
        return PhoneCallResult(
            status=PhoneCallStatus.SUCCESS,
            request_id=call_id,
            provider="mock",
        )


# TranscriptExtractor is reused from the callee provider so mock and real
# providers normalize transcripts identically.
__all__ = ["MockProvider", "TranscriptExtractor"]