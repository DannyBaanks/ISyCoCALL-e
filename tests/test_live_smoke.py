"""LIVE smoke test.

This test is the ONLY one that contacts the real CALL-E API and can place a
REAL PHONE CALL. It is skipped unless CALLE_API_KEY is set AND CALL_E_LIVE=1
is explicitly provided. Never run with a mock; a mock here would be presented
as live evidence, which is forbidden.

Guard:        tests skip unless CALLE_API_KEY present.
Live gate:    call is only placed if CALL_E_LIVE=1 (extra safety).
"""

import os
import pytest

from isyco_calle.domain.contract import CAPABILITY_PHONE_CALL, PhoneCallRequest
from isyco_calle.providers.callee import CalleProvider
from isyco_calle.domain.result import PhoneCallStatus


@pytest.mark.skipif(
    not os.environ.get("CALLE_API_KEY"),
    reason="LIVE: CALLE_API_KEY not set -> no real call can be placed",
)
def test_doctor_with_live_credentials():
    """Config + SDK wiring check that requires a real API key but places NO call."""
    provider = CalleProvider()
    checks = provider._doctor()
    assert checks["config"] == "ok"
    assert checks["sdk"] == "ok"


@pytest.mark.skipif(
    not (os.environ.get("CALLE_API_KEY") and os.environ.get("CALL_E_LIVE") == "1"),
    reason="LIVE: requires CALLE_API_KEY and CALL_E_LIVE=1 (real call)",
)
def test_real_call_end_to_end():
    """Places a REAL call. This is live evidence, not a mock.

    Calls the well-known test number / a consented fixture destination. Run
    ONLY with an account that can spend a call and a number you control.
    """
    request = PhoneCallRequest(
        action=CAPABILITY_PHONE_CALL,
        objective=os.environ.get("CALL_E_TEST_OBJECTIVE", "Say hello and confirm the line is a test."),
        phone=os.environ["CALL_E_TEST_PHONE"],
        result_schema={
            "type": "object",
            "required": ["reached"],
            "properties": {"reached": {"type": "string", "enum": ["yes", "no"]}},
        },
    )
    provider = CalleProvider()
    result = provider.place_and_wait(request)
    assert result.status is PhoneCallStatus.SUCCESS
    assert result.request_id is not None