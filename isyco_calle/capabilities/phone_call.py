"""The `phone.call` capability.

Orchestrates the vertical slice for a single call:
    contract -> authority -> provider -> structured result

`capability != authority`: this capability is only *made available* here. It
refuses to dispatch unless an AuthorityEvaluator grants it along all four axes.
"""

from __future__ import annotations

from typing import Callable, Optional, Protocol, runtime_checkable

from ..domain.authority import AuthorityEvaluator, AuthorityDecision
from ..domain.contract import PhoneCallRequest
from ..domain.result import PhoneCallResult, PhoneCallStatus


@runtime_checkable
class CallProvider(Protocol):
    """Minimal seam a real provider adapter must satisfy."""

    def place_and_wait(self, request: PhoneCallRequest) -> PhoneCallResult: ...

    def get(self, call_id: str) -> PhoneCallResult: ...


class PhoneCallCapability:
    """Exposes `phone.call` to callers; never calls without authority."""

    NAME = "phone.call"

    def __init__(
        self,
        provider: CallProvider,
        authority: AuthorityEvaluator,
        verify_fn: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self._provider = provider
        self._authority = authority
        # verify_fn: explicit execution-confirmation callback (default: denied).
        self._verify_fn = verify_fn or (lambda caller: False)

    def call(
        self,
        request: PhoneCallRequest,
        *,
        caller: str,
        scopes: frozenset[str] = frozenset(),
    ) -> PhoneCallResult:
        request.validate()

        check = self._authority.evaluate(
            caller=caller,
            capability=self.NAME,
            scopes=scopes,
            _verified=self._verify_fn(caller),
        )
        if check.decision() is AuthorityDecision.DENY:
            return PhoneCallResult(
                status=PhoneCallStatus.REJECTED,
                error=f"authority denied: {check.to_dict()['reasons']}",
            )
        try:
            return self._provider.place_and_wait(request)
        except Exception as exc:  # safety net: replaceable providers may throw
            return PhoneCallResult(
                status=PhoneCallStatus.PROVIDER_ERROR,
                error=f"{type(exc).__name__}: {exc}",
            )

    def status(self, call_id: str) -> PhoneCallResult:
        return self._provider.get(call_id)