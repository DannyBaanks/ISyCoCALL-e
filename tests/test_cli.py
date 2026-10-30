import json
from argparse import Namespace

import pytest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from isyco_calle import cli
from isyco_calle import demo
from isyco_calle.domain.authority import CapabilityGrant, sign_grant
from isyco_calle.domain.result import PhoneCallResult, PhoneCallStatus


def test_result_schema_is_parsed_as_json_object():
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "call", "--to", "+15555550123", "--objective", "x", "--mock", "--allow",
            "--result-schema", '{"type":"object"}',
        ]
    )
    assert args.result_schema == {"type": "object"}


def test_real_call_requires_idempotency_key():
    args = Namespace(
        mock=False, idempotency_key=None, objective="x", to="+15555550123",
        result_schema=None, region=None, locale=None, caller="alice", allow=True,
        grant_file=None,
    )
    with pytest.raises(Exception, match="idempotency"):
        cli.cmd_call(args)


def test_provider_error_has_nonzero_exit(monkeypatch, capsys):
    class FailingCapability:
        def status(self, *_args, **_kwargs):
            return PhoneCallResult.provider_error("synthetic")

    monkeypatch.setattr(cli, "_capability", lambda **_kwargs: FailingCapability())
    args = Namespace(
        mock=False, call_id="call_x", caller="alice", allow=True,
        grant_file="grant.json",
    )
    assert cli.cmd_status(args) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "provider_error"


def test_not_demonstrated_has_nonzero_exit():
    assert cli._exit_code(PhoneCallStatus.NOT_DEMONSTRATED) != 0


def test_load_grant_verifies_signature_and_caller(tmp_path, monkeypatch):
    key = Ed25519PrivateKey.generate()
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    grant = CapabilityGrant(
        "alice", "phone.call", expires_at="2099-01-01T00:00:00Z",
        scopes=frozenset({"phone:+15555550123"}),
    )
    receipt = {
        "algorithm": "ed25519",
        "grant": grant.to_dict(),
        "signature": sign_grant(grant, private_pem),
    }
    path = tmp_path / "grant.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    monkeypatch.setattr(cli, "TRUSTED_GRANT_PUBLIC_KEY_PEM", public_pem)
    load = lambda caller: cli._load_grant(
        str(path), caller,
        expected_capability="phone.call", required_scope="phone:+15555550123",
    )
    assert load("alice") == grant
    with pytest.raises(Exception, match="caller"):
        load("mallory")


def test_mock_status_requires_explicit_confirmation():
    base = Namespace(
        mock=True, call_id="mock_x", caller="alice", grant_file=None,
    )
    assert cli.cmd_status(Namespace(**vars(base), allow=False)) == 2
    assert cli.cmd_status(Namespace(**vars(base), allow=True)) == 0


def test_real_demo_path_is_disabled():
    assert demo.run(real=True) == 2


@pytest.mark.parametrize(
    ("expires_at", "scope", "message"),
    [
        (None, "phone:+15555550123", "must expire"),
        ("2099-01-01T00:00:00Z", "phone:+15555550999", "resource scope"),
    ],
)
def test_real_grant_requires_expiry_and_exact_resource(
    tmp_path, monkeypatch, expires_at, scope, message
):
    key = Ed25519PrivateKey.generate()
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    grant = CapabilityGrant(
        "alice", "phone.call", expires_at=expires_at, scopes=frozenset({scope})
    )
    receipt = {
        "algorithm": "ed25519",
        "grant": grant.to_dict(),
        "signature": sign_grant(grant, private_pem),
    }
    receipt_path = tmp_path / "grant.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    monkeypatch.setattr(cli, "TRUSTED_GRANT_PUBLIC_KEY_PEM", public_pem)
    with pytest.raises(Exception, match=message):
        cli._load_grant(
            str(receipt_path), "alice",
            expected_capability="phone.call", required_scope="phone:+15555550123",
        )


@pytest.mark.parametrize(
    ("capability", "scope", "prefix"),
    [("phone.call", "call:abc", "phone:"), ("phone.call.status", "phone:+1", "call:")],
)
def test_grant_issuer_rejects_wrong_resource_scope(capability, scope, prefix):
    args = Namespace(
        caller="alice", capability=capability, expires_at="2099-01-01T00:00:00Z",
        scope=[scope], policy="default", private_key_file="unused.pem", out="unused.json",
    )
    with pytest.raises(Exception, match=prefix):
        cli.cmd_grant_issue(args)


def test_default_caller_honors_environment(monkeypatch):
    monkeypatch.setenv("ISYCO_CALL_DEFAULT_CALLER", "trusted-launcher")
    args = cli.build_parser().parse_args(
        ["call", "--to", "+15555550123", "--objective", "x", "--mock"]
    )
    assert args.caller == "trusted-launcher"
