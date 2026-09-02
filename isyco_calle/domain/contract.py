"""Contract: what the caller asks for.

Defines the normalized, provider-agnostic request that ISyCo accepts for the
`phone.call` capability. CALL-E must NOT contaminate this higher-level
contract: the caller does not need to know about CALL-E to express a call.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


class ContractError(ValueError):
    """Raised when a phone call request is malformed."""


# Loosely matches E.164: +<1-3 digits country><national>. Not a strict validator.
_E164_RE = re.compile(r"^\+[1-9][0-9]{6,14}$")

# Capability name is fixed and enforced at the boundary.
CAPABILITY_PHONE_CALL = "phone.call"


@dataclass(frozen=True)
class PhoneCallRequest:
    """A normalized, provider-agnostic request to place a phone call.

    Only fields ISyCo's upper layer cares about. Provider-specific details
    (e.g. CALL-E recipient envelope) are derived in the adapter, not here.
    """

    action: str
    objective: str
    phone: str
    result_schema: Optional[Dict[str, Any]] = None
    region: Optional[str] = None
    locale: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    idempotency_key: Optional[str] = None

    def validate(self) -> "PhoneCallRequest":
        if self.action != CAPABILITY_PHONE_CALL:
            raise ContractError(
                f"unsupported action {self.action!r}; expected {CAPABILITY_PHONE_CALL!r}"
            )
        if not self.objective or not self.objective.strip():
            raise ContractError("objective must be a non-empty string")
        if not self._valid_e164(self.phone):
            raise ContractError(f"phone must be a valid E.164 number, got {self.phone!r}")
        return self

    @staticmethod
    def _valid_e164(phone: str) -> bool:
        return bool(phone) and bool(_E164_RE.match(phone.strip()))

    def task_text(self) -> str:
        """The natural-language task sent to a provider's execution engine."""
        return self.objective.strip()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhoneCallRequest":
        target = data.get("target") or {}
        if not isinstance(target, dict):
            raise ContractError("target must be an object")
        phone = target.get("phone") or data.get("phone")
        try:
            req = cls(
                action=str(data.get("action") or CAPABILITY_PHONE_CALL),
                objective=str(data.get("objective") or ""),
                phone=str(phone or ""),
                result_schema=data.get("result_schema"),
                region=data.get("region"),
                locale=data.get("locale"),
                metadata=dict(data.get("metadata") or {}),
                idempotency_key=data.get("idempotency_key"),
            )
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ContractError(f"malformed request: {exc}") from exc
        return req.validate()


class InputContract:
    """Boundary wrapper that validates caller input before any authority or
    provider logic runs."""

    def __init__(self) -> None:
        self._schema = {
            "type": "object",
            "required": ["action", "objective", "target"],
            "properties": {
                "action": {"const": CAPABILITY_PHONE_CALL},
                "objective": {"type": "string", "minLength": 1},
                "target": {
                    "type": "object",
                    "required": ["phone"],
                    "properties": {"phone": {"type": "string", "pattern": r"^\+[1-9][0-9]{6,14}$"}},
                },
            },
        }

    def schema(self) -> Dict[str, Any]:
        return self._schema

    def parse(self, data: Dict[str, Any]) -> PhoneCallRequest:
        return PhoneCallRequest.from_dict(data)