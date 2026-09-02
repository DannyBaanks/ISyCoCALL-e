"""Result: the normalized answer ISyCo returns to the caller.

The result must be able to distinguish at least:
    success, failed, rejected, timeout, provider_error, not_demonstrated
It carries only metadata actually made available by the provider. Fields that
a provider does not supply stay None (they are not invented).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PhoneCallStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    NOT_DEMONSTRATED = "not_demonstrated"

    def __str__(self) -> str:  # ergonomic in logs / CLI
        return self.value


@dataclass(frozen=True)
class PhoneCallResult:
    """Normalized, provider-agnostic outcome of a phone call."""

    status: PhoneCallStatus
    request_id: Optional[str] = None
    provider: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    structured_output: Optional[Dict[str, Any]] = None
    completion_confidence: Optional[Dict[str, Any]] = None
    raw_evidence_reference: Optional[List[str]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "request_id": self.request_id,
            "provider": self.provider,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "transcript": self.transcript,
            "summary": self.summary,
            "structured_output": self.structured_output,
            "completion_confidence": self.completion_confidence,
            "raw_evidence_reference": self.raw_evidence_reference,
            "error": self.error,
        }

    @classmethod
    def not_demonstrated(cls, reason: str = "") -> "PhoneCallResult":
        return cls(status=PhoneCallStatus.NOT_DEMONSTRATED, error=reason or None)

    @classmethod
    def provider_error(cls, error: str) -> "PhoneCallResult":
        return cls(status=PhoneCallStatus.PROVIDER_ERROR, error=error)