"""Golden demo: one command that shows the two honest paths.

DENIED: no caller authority -> rejected, no call placed.
AUTHORIZED: explicit grant -> real provider call.

Mock provider by default. Real CALL-E requires CALLE_API_KEY and --real.
"""

from __future__ import annotations

import sys

from .capabilities.phone_call import PhoneCallCapability
from .config import Settings
from .domain.authority import AuthorityEvaluator, CapabilityGrant
from .domain.contract import CAPABILITY_PHONE_CALL, PhoneCallRequest
from .providers.mock import MockProvider

DEMO_TO = "+15555550142"
DEMO_OBJECTIVE = "Confirm whether the business is open tomorrow"
DEMO_CALLER = "demo-user"


def _hr(title: str) -> None:
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def _request() -> PhoneCallRequest:
    return PhoneCallRequest(
        action=CAPABILITY_PHONE_CALL,
        objective=DEMO_OBJECTIVE,
        phone=DEMO_TO,
        result_schema={
            "type": "object",
            "required": ["open_tomorrow"],
            "properties": {"open_tomorrow": {"type": "string", "enum": ["yes", "no", "unknown"]}},
        },
    )


def run(*, real: bool = False) -> int:
    print("ISyCo CALL Bridge — golden demo")
    print("(mock provider unless --real and CALLE_API_KEY is set)")
    print()
    print("[request]")
    print(f"  objective : {DEMO_OBJECTIVE}")
    print(f"  target    : {DEMO_TO}")

    # ---------- PATH A: DENIED ----------
    _hr("PATH A — denied (no authority grant)")
    requests: list[str] = []
    mock_a = MockProvider()
    cap = PhoneCallCapability(provider=mock_a, authority=AuthorityEvaluator())
    result = cap.call(_request(), caller=DEMO_CALLER)
    print("[authority] no grant present")
    print(f"[result]    status = {result.status.value}")
    if result.error:
        print(f"[detail]    {result.error}")
    print(f"[fact]      provider touched = {len(mock_a.requests) > 0}")

    # ---------- PATH B: AUTHORIZED ----------
    _hr("PATH B — authorized")
    authority = AuthorityEvaluator()
    authority.grant(CapabilityGrant(caller=DEMO_CALLER, capability=CAPABILITY_PHONE_CALL))

    if real:
        from .providers.callee import CalleProvider
        settings = Settings.load()
        try:
            settings.validate()
        except Exception as exc:
            print(f"[real] CALLE_API_KEY missing or unusable: {exc}")
            print("       rerun without --real for the mock, or export a real key.")
            return 1
        provider = CalleProvider(settings)
        label = "CALL-E (real)"
    else:
        provider = MockProvider()
        label = "mock"

    cap = PhoneCallCapability(provider=provider, authority=authority,
                              verify_fn=lambda _caller: True)
    print(f"[authority] grant issued; verified = true")
    granted_result = cap.call(_request(), caller=DEMO_CALLER)
    r = granted_result.to_dict()
    print(f"[provider]  {label}")
    print(f"[result]    status = {r['status']}")
    print(f"            request_id = {r['request_id']}")
    print(f"            structured_output = {r['structured_output']}")
    if r["raw_evidence_reference"]:
        print(f"            evidence = {r['raw_evidence_reference']}")

    _hr("SUMMARY")
    print(f"  denied  -> no call      (provider untouched: {len(mock_a.requests) == 0})")
    print(f"  granted -> {r['status']} via {label} ({r['request_id']})")
    return 0


if __name__ == "__main__":
    sys.exit(run(real="--real" in sys.argv))
