"""CALL-E provider adapter (REAL integration).

Wraps the official Python SDK `calle-ai` (CalleClient). This is the actual
runtime integration with CALL-E; it is kept separate from the upper contract
and only surfaces normalized PhoneCallResult objects, so CALL-E does not
contaminate the higher-level contract.

A real call is placed only when place_and_wait() is invoked with a valid
request AND the capability layer has already granted authority.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..domain.contract import PhoneCallRequest
from ..domain.result import PhoneCallResult, PhoneCallStatus
from ..config import ConfigError, Settings


class TranscriptExtractor:
    """Pulls a plain-text transcript out of a CALL-E result.

    CALL-E returns transcript turns under recipients[].attempts[]
    .transcript_turns[] as [{offset_seconds, speaker, text}]. We flatten them
    into readable lines. If the shape is not present, transcript stays None
    rather than being invented.
    """

    @classmethod
    def extract(cls, call: Dict[str, Any]) -> Optional[str]:
        recipients = call.get("recipients")
        if not isinstance(recipients, list) or not recipients:
            return None
        lines: List[str] = []
        for recipient in recipients:
            attempts = recipient.get("attempts") or []
            for attempt in attempts:
                turns = attempt.get("transcript_turns") or []
                for turn in turns:
                    speaker = str(turn.get("speaker", "?"))
                    text = str(turn.get("text", ""))
                    lines.append(f"[{speaker}] {text}")
        return "\n".join(lines) if lines else None


class CalleProvider:
    """Adapter over the official `calle-ai` SDK."""

    PROVIDER = "calle"

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or Settings.load()
        self._client: Any = None  # lazily built so `doctor` works without SDK issues

    @property
    def client(self) -> Any:
        if self._client is None:
            try:
                from calle import CalleClient
            except ImportError as exc:  # pragma: no cover - env dependent
                raise ConfigError(
                    "calle-ai SDK not installed; run: pip install calle-ai"
                ) from exc
            self._client = CalleClient(
                api_key=self._settings.calle_api_key,
                base_url=self._settings.calle_base_url,
                timeout=self._settings.calle_timeout,
            )
        return self._client

    def _recipient(self, request: PhoneCallRequest) -> Dict[str, Any]:
        recipient: Dict[str, Any] = {"phones": [request.phone]}
        if request.region:
            recipient["region"] = request.region
        if request.locale:
            recipient["locale"] = request.locale
        return recipient

    def place_and_wait(self, request: PhoneCallRequest) -> PhoneCallResult:
        request.validate()
        try:
            call = self.client.calls.create_and_wait(
                task=request.task_text(),
                recipient=self._recipient(request),
                result_schema=request.result_schema,
                metadata=request.metadata or None,
                idempotency_key=request.idempotency_key,
            )
        except Exception as exc:  # provider/network boundary -> normalized error
            return self._from_exception(exc)
        return self._from_call(call)

    def get(self, call_id: str) -> PhoneCallResult:
        try:
            call = self.client.calls.get(call_id)
        except Exception as exc:  # pragma: no cover - depends on live API
            return self._from_exception(exc)
        return self._from_call(call)

    # -- mapping helpers ---------------------------------------------------

    def _from_exception(self, exc: Exception) -> PhoneCallResult:
        try:
            from calle import (
                CalleTimeoutError,
                CalleConnectionError,
                CalleAuthenticationError,
            )
        except ImportError:  # pragma: no cover - env dependent
            CalleTimeoutError = CalleConnectionError = CalleAuthenticationError = (None,)

        msg = f"{type(exc).__name__}: {exc}"
        if CalleTimeoutError is not None and isinstance(exc, CalleTimeoutError):
            return PhoneCallResult(status=PhoneCallStatus.TIMEOUT, error=msg)
        if CalleConnectionError is not None and isinstance(exc, CalleConnectionError):
            return PhoneCallResult(status=PhoneCallStatus.PROVIDER_ERROR, error=msg)
        if CalleAuthenticationError is not None and isinstance(exc, CalleAuthenticationError):
            return PhoneCallResult(status=PhoneCallStatus.REJECTED, error=msg)
        return PhoneCallResult(status=PhoneCallStatus.PROVIDER_ERROR, error=msg)

    def _from_call(self, call: Dict[str, Any]) -> PhoneCallResult:
        status = call.get("status")
        task_completed = bool(call.get("task_completed"))

        if status == "completed" and task_completed:
            outcome = PhoneCallStatus.SUCCESS
        elif status in ("completed", "failed"):
            outcome = PhoneCallStatus.FAILED
        elif status == "canceled":
            outcome = PhoneCallStatus.REJECTED
        else:
            # Unknown/incomplete terminal shape -> do not invent a conclusion.
            outcome = PhoneCallStatus.NOT_DEMONSTRATED

        # Carrier-level detail discovered live on 2026-09-03 (issue #105):
        # a run may end with status "NO ANSWER" while the handset never rang
        # (hangup_type=ByCallee, duration_seconds=0). _build_evidence_refs
        # surfaces it instead of inventing a nicer story.
        return PhoneCallResult(
            status=outcome,
            request_id=call.get("id"),
            provider=self.PROVIDER,
            started_at=call.get("started_at"),
            finished_at=call.get("finished_at"),
            transcript=TranscriptExtractor.extract(call),
            summary=call.get("summary"),
            structured_output=call.get("structured_result") or call.get("result", {}).get("extracted"),
            completion_confidence=call.get("completion_confidence")
            or call.get("result", {}).get("outcome", {}).get("completion_confidence"),
            raw_evidence_reference=self._build_evidence_refs(call),
        )

    def _extract_carrier_evidence(self, call: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Pull carrier-side hangup detail when present (live runs expose this).

        Observed in real CALL-E runs: run.result.extracted.calling.calls[].
        """
        result = call.get("result") or {}
        extracted = result.get("extracted") or {}
        calling = extracted.get("calling") or {}
        calls = calling.get("calls") or []
        if calls and isinstance(calls[0], dict):
            return calls[0]
        return None

    def _build_evidence_refs(self, call: Dict[str, Any]) -> Optional[list]:
        refs: list = []
        evidence = call.get("evidence")
        if evidence:
            refs.extend(evidence if isinstance(evidence, list) else [str(evidence)])
        carrier = self._extract_carrier_evidence(call)
        if carrier is not None:
            refs.append(
                f"carrier: hangup={carrier.get('hangup_type')} duration={carrier.get('duration_seconds')}s"
            )
        return refs or None

    def _doctor(self) -> Dict[str, Any]:
        """Check config/SDK wiring without placing a call."""
        checks: Dict[str, Any] = {"provider": self.PROVIDER}
        try:
            self._settings.validate()
            checks["config"] = "ok"
        except ConfigError as exc:
            checks["config"] = f"error: {exc}"
        try:
            _ = self.client
            checks["sdk"] = "ok"
        except ConfigError as exc:
            checks["sdk"] = f"error: {exc}"
        return checks