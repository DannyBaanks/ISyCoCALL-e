import pytest

from isyco_calle.domain.result import PhoneCallResult, PhoneCallStatus


def test_all_required_statuses_exist():
    required = {"success", "failed", "rejected", "timeout", "provider_error", "not_demonstrated"}
    assert required.issubset({s.value for s in PhoneCallStatus})


def test_result_to_dict_roundtrip():
    r = PhoneCallResult(
        status=PhoneCallStatus.SUCCESS,
        request_id="call_123",
        provider="calle",
        structured_output={"open": "yes"},
        raw_evidence_reference=["they said yes"],
    )
    d = r.to_dict()
    assert d["status"] == "success"
    assert d["request_id"] == "call_123"
    assert d["structured_output"] == {"open": "yes"}


def test_not_demonstrated_factory():
    r = PhoneCallResult.not_demonstrated("no credentials")
    assert r.status is PhoneCallStatus.NOT_DEMONSTRATED
    assert r.error == "no credentials"


def test_provider_error_factory():
    r = PhoneCallResult.provider_error("boom")
    assert r.status is PhoneCallStatus.PROVIDER_ERROR


def test_absent_fields_stay_none():
    r = PhoneCallResult(status=PhoneCallStatus.FAILED)
    d = r.to_dict()
    assert d["transcript"] is None
    assert d["completion_confidence"] is None