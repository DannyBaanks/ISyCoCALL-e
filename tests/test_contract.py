import pytest

from isyco_calle.domain.contract import (
    CAPABILITY_PHONE_CALL,
    ContractError,
    InputContract,
    PhoneCallRequest,
)


def test_parse_valid_request():
    data = {
        "action": CAPABILITY_PHONE_CALL,
        "objective": "Confirm whether a business is open tomorrow",
        "target": {"phone": "+12025550123"},
        "result_schema": {"type": "object", "required": ["open"], "properties": {"open": {"type": "string"}}},
    }
    req = InputContract().parse(data)
    assert req.objective.startswith("Confirm")
    assert req.phone == "+12025550123"
    assert req.result_schema is not None


def test_parse_accepts_nested_target_and_top_level_phone():
    req = PhoneCallRequest.from_dict(
        {
            "action": CAPABILITY_PHONE_CALL,
            "objective": "x",
            "target": {"phone": "+15555550123"},
        }
    )
    assert req.phone == "+15555550123"


def test_rejects_wrong_action():
    with pytest.raises(ContractError):
        InputContract().parse({"action": "send.email", "objective": "x", "target": {"phone": "+15555550123"}})


def test_rejects_missing_phone():
    with pytest.raises(ContractError):
        InputContract().parse({"action": CAPABILITY_PHONE_CALL, "objective": "x", "target": {}})


def test_rejects_empty_objective():
    with pytest.raises(ContractError):
        InputContract().parse({"action": CAPABILITY_PHONE_CALL, "objective": " ", "target": {"phone": "+15555550123"}})


def test_rejects_non_e164_phone():
    with pytest.raises(ContractError):
        PhoneCallRequest(action=CAPABILITY_PHONE_CALL, objective="x", phone="123-456").validate()


def test_schema_has_expected_shape():
    schema = InputContract().schema()
    assert schema["required"] == ["action", "objective", "target"]
    assert schema["properties"]["action"]["const"] == CAPABILITY_PHONE_CALL


def test_task_text_is_objective():
    req = PhoneCallRequest(action=CAPABILITY_PHONE_CALL, objective="  call them  ", phone="+15555550123")
    assert req.task_text() == "call them"