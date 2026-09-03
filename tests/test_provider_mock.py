"""Adapter tests with an EXPLICIT mock (the MockProvider).

These never touch the network and never place a call. The real CALL-E adapter
is exercised by test_live_smoke.py, which is marked LIVE and skipped without
credentials.
"""

import pytest

from isyco_calle.capabilities.phone_call import PhoneCallCapability
from isyco_calle.domain.authority import AuthorityEvaluator, CapabilityGrant
from isyco_calle.domain.contract import CAPABILITY_PHONE_CALL, PhoneCallRequest
from isyco_calle.domain.result import PhoneCallStatus
from isyco_calle.providers.mock import MockProvider


def _request(**kw):
    base = dict(
        action=CAPABILITY_PHONE_CALL,
        objective="Confirm a business is open tomorrow",
        phone="+12025550123",
    )
    base.update(kw)
    return PhoneCallRequest(**base)


def test_authority_deny_returns_rejected_and_calls_nothing():
    provider = MockProvider()
    authority = AuthorityEvaluator()  # no grant
    cap = PhoneCallCapability(provider=provider, authority=authority, verify_fn=lambda _c: True)
    result = cap.call(_request(), caller="alice")
    assert result.status is PhoneCallStatus.REJECTED
    assert provider.requests == []  # no provider touched


def test_authority_allow_dispatches_to_provider():
    provider = MockProvider()
    authority = AuthorityEvaluator()
    authority.grant(CapabilityGrant(caller="alice", capability=CAPABILITY_PHONE_CALL))
    cap = PhoneCallCapability(provider=provider, authority=authority, verify_fn=lambda _c: True)
    result = cap.call(_request(), caller="alice")
    assert result.status is PhoneCallStatus.SUCCESS
    assert len(provider.requests) == 1
    assert provider.requests[0].phone == "+12025550123"


def test_unverified_grant_is_denied():
    provider = MockProvider()
    authority = AuthorityEvaluator()
    authority.grant(CapabilityGrant(caller="alice", capability=CAPABILITY_PHONE_CALL))
    cap = PhoneCallCapability(provider=provider, authority=authority, verify_fn=lambda _c: False)
    result = cap.call(_request(), caller="alice")
    assert result.status is PhoneCallStatus.REJECTED
    assert provider.requests == []


def test_provider_error_maps_to_provider_error():
    provider = MockProvider()
    provider.raise_error = RuntimeError("network down")
    authority = AuthorityEvaluator()
    authority.grant(CapabilityGrant(caller="alice", capability=CAPABILITY_PHONE_CALL))
    cap = PhoneCallCapability(provider=provider, authority=authority, verify_fn=lambda _c: True)
    result = cap.call(_request(), caller="alice")
    assert result.status is PhoneCallStatus.PROVIDER_ERROR


def test_status_via_capability():
    provider = MockProvider()
    cap = PhoneCallCapability(provider=provider, authority=AuthorityEvaluator())
    result = cap.status("mock_abc")
    assert result.request_id == "mock_abc"
    assert result.status is PhoneCallStatus.SUCCESS


# -- carrier evidence extraction from REAL observed shape -------------

def test_carrier_evidence_extracted_from_real_shape():
    """Patch with the actual observed response structure from #105 evidence."""
    from isyco_calle.providers.callee import CalleProvider
    provider = CalleProvider.__new__(CalleProvider)
    call = {
        "status": "failed",
        "id": "call_x",
        "result": {
            "extracted": {
                "calling": {
                    "calls": [
                        {
                            "status": "NO ANSWER",
                            "hangup_type": "ByCallee",
                            "duration_seconds": 0,
                            "call_start_time": "2026-09-03 01:41:51",
                            "call_end_time": "2026-09-03 01:41:51",
                        }
                    ]
                }
            }
        },
    }
    carrier = provider._extract_carrier_evidence(call)
    assert carrier["hangup_type"] == "ByCallee"
    refs = provider._build_evidence_refs(call)
    assert any("ByCallee" in r for r in refs)


def test_no_carrier_evidence_when_absent():
    from isyco_calle.providers.callee import CalleProvider
    provider = CalleProvider.__new__(CalleProvider)
    refs = provider._build_evidence_refs({"status": "completed", "task_completed": True, "evidence": ["a"]})
    assert refs == ["a"]

def test_transcript_extractor_flattens_turns():
    from isyco_calle.providers.callee import TranscriptExtractor
    call = {
        "recipients": [
            {
                "attempts": [
                    {
                        "transcript_turns": [
                            {"offset_seconds": 0, "speaker": "bot", "text": "Hi"},
                            {"offset_seconds": 4, "speaker": "user", "text": "Yes"},
                        ]
                    }
                ]
            }
        ]
    }
    assert TranscriptExtractor.extract(call) == "[bot] Hi\n[user] Yes"


def test_transcript_extractor_none_when_absent():
    from isyco_calle.providers.callee import TranscriptExtractor
    assert TranscriptExtractor.extract({"recipients": []}) is None
    assert TranscriptExtractor.extract({}) is None