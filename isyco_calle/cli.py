"""ISyCo CALL Bridge - CLI.

Minimal executable surface:
    isyco-call doctor
    isyco-call call --to +... --objective "..."
    isyco-call status <call_id>

Runs with `py -m isyco_calle.cli` (bare `python` is intercepted by the ISyCo
evo-guard shim on the authoring workstation). The `call` subcommand refuses to
execute unless authority is granted (explicit verification flag + grant).
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from .config import Settings
from .domain.authority import AuthorityEvaluator, CapabilityGrant
from .domain.contract import CAPABILITY_PHONE_CALL, PhoneCallRequest
from .providers.callee import CalleProvider
from .providers.mock import MockProvider
from .capabilities.phone_call import PhoneCallCapability


def _capability(
    *, caller: str, use_mock: bool, allow: bool, region: Optional[str]
) -> PhoneCallCapability:
    authority = AuthorityEvaluator()
    if use_mock:
        provider = MockProvider()  # type: ignore[assignment]
    else:
        provider = CalleProvider()  # type: ignore[assignment]
    authority.grant(
        CapabilityGrant(
            caller=caller,
            capability=CAPABILITY_PHONE_CALL,
            scopes=frozenset({region}) if region else frozenset(),
        )
    )
    return PhoneCallCapability(
        provider=provider,  # type: ignore[arg-type]
        authority=authority,
        verify_fn=lambda _c: allow,
    )


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, default=str))


def cmd_doctor(args) -> int:
    settings = Settings.load()
    checks = {"cli": "ok", "config": None, "sdk": None}
    try:
        settings.validate()
        checks["config"] = "ok"
    except Exception as exc:
        checks["config"] = f"error: {exc}"
    provider = CalleProvider(settings)
    sdk = provider._doctor()
    checks["sdk"] = sdk.get("sdk")
    checks["provider"] = sdk.get("provider")
    checks["base_url"] = settings.calle_base_url
    checks["env_var"] = "CALLE_API_KEY"
    _print({"command": "doctor", **checks})
    return 0 if checks["config"] == "ok" and checks["sdk"] == "ok" else 1


def cmd_call(args) -> int:
    settings = Settings.load()
    request = PhoneCallRequest(
        action=CAPABILITY_PHONE_CALL,
        objective=args.objective,
        phone=args.to,
        result_schema=args.result_schema,
        region=args.region,
        locale=args.locale,
        metadata={"cli": True},
        idempotency_key=args.idempotency_key,
    ).validate()

    cap = _capability(
        caller=args.caller,
        use_mock=args.mock,
        allow=args.allow,
        region=args.region,
    )
    result = cap.call(
        request,
        caller=args.caller,
        scopes=frozenset({args.region}) if args.region else frozenset(),
    )
    _print({"command": "call", **result.to_dict()})
    return 0 if result.status.value in ("success", "not_demonstrated") else 2


def cmd_status(args) -> int:
    provider = MockProvider() if args.mock else CalleProvider()
    result = provider.get(args.call_id)
    _print({"command": "status", **result.to_dict()})
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="isyco-call", description="ISyCo CALL Bridge")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("doctor", help="check config + SDK wiring (no call placed)")
    d.set_defaults(func=cmd_doctor)

    c = sub.add_parser("call", help="place a phone call (authority-gated)")
    c.add_argument("--to", required=True, help="E.164 phone number, e.g. +120255501234")
    c.add_argument("--objective", required=True, help="what the call should accomplish")
    c.add_argument("--result-schema", help="JSON result_schema passed to CALL-E")
    c.add_argument("--region", help="two-letter region, e.g. US")
    c.add_argument("--locale", help="locale, e.g. en-US")
    c.add_argument("--idempotency-key", help="stable idempotency key")
    c.add_argument("--caller", default="cli", help="caller identity for authority check")
    c.add_argument(
        "--allow",
        action="store_true",
        help="explicitly confirm the call for execution (the `verified` axis)",
    )
    c.add_argument("--mock", action="store_true", help="use the in-memory mock provider (tests only)")
    c.set_defaults(func=cmd_call)

    s = sub.add_parser("status", help="read a call result by id")
    s.add_argument("call_id", help="CALL-E call id")
    s.add_argument("--mock", action="store_true", help="use mock provider (tests only)")
    s.set_defaults(func=cmd_status)

    return p


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:  # surface a clean JSON error
        _print({"command": args.command, "error": f"{type(exc).__name__}: {exc}"})
        return 2


if __name__ == "__main__":
    sys.exit(main())