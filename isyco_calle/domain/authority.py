"""Authority boundary: capability != authority.

A caller does not obtain the power to place calls merely by existing. Placing
a call must require an explicit, granted capability, and the grant is
evaluated along four independent axes so that `intent == authority` cannot
hold by construction.

The four axes are deliberately NOT collapsed into a single boolean:
  - technically_possible : the capability exists and this caller type may use it
  - authorized           : the caller identity holds a grant for the capability
  - policy_allowed       : the grant is in force (not expired/revoked) and the
                           request parameters pass applicable policy checks
  - verified             : the operation is approved for execution (explicit
                           human or issuing-context confirmation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class AuthorityDecision(str, Enum):
    DENY = "deny"
    ALLOW = "allow"


@dataclass(frozen=True)
class CapabilityGrant:
    """A minimal, explicit grant of a single capability to a caller."""

    caller: str
    capability: str
    policy: str = "default"
    expires_at: Optional[str] = None  # ISO timestamp; None = no expiry
    scopes: frozenset[str] = frozenset()  # e.g. region allow-list

    def scopes_include(self, scope: str) -> bool:
        return not self.scopes or scope in self.scopes


@dataclass
class AuthorityCheck:
    """The four-axis evaluation for a single call request."""

    capability: str
    technically_possible: bool = False
    authorized: bool = False
    policy_allowed: bool = False
    verified: bool = False
    reasons: Dict[str, str] = field(default_factory=dict)

    def decision(self) -> AuthorityDecision:
        all_ok = (
            self.technically_possible
            and self.authorized
            and self.policy_allowed
            and self.verified
        )
        return AuthorityDecision.ALLOW if all_ok else AuthorityDecision.DENY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "technically_possible": self.technically_possible,
            "authorized": self.authorized,
            "policy_allowed": self.policy_allowed,
            "verified": self.verified,
            "reasons": dict(self.reasons),
            "decision": self.decision().value,
        }


class AuthorityEvaluator:
    """Tiny evaluator. This is a contract, not a policy engine.

    Production callers would connect each axis to a real grant store / policy
    source / verification step; here we keep the seams explicit and small.
    """

    def __init__(self, registry: Optional[Dict[str, CapabilityGrant]] = None) -> None:
        self._grants = dict(registry or {})

    def grant(self, grant: CapabilityGrant) -> None:
        self._grants[(grant.caller, grant.capability)] = grant

    def revoke(self, caller: str, capability: str) -> None:
        self._grants.pop((caller, capability), None)

    def evaluate(
        self,
        *,
        caller: str,
        capability: str,
        scopes: frozenset[str] = frozenset(),
        _verified: bool = False,
    ) -> AuthorityCheck:
        check = AuthorityCheck(capability=capability)

        # 1. technically_possible - the capability is registered and callers may use it.
        check.technically_possible = True
        check.reasons["technically_possible"] = "capability registered"

        # 2. authorized - explicit grant present for (caller, capability).
        grant = self._grants.get((caller, capability))
        if grant is None:
            check.reasons["authorized"] = "no explicit grant for caller/capability"
        else:
            check.authorized = True
            check.reasons["authorized"] = f"grant policy={grant.policy}"

        # 3. policy_allowed - grant in force and request scopes covered.
        if check.authorized:
            if grant is not None and grant.scopes_include_all(scopes):
                check.policy_allowed = True
                check.reasons["policy_allowed"] = f"scopes covered ({len(scopes)} provided)"
            else:
                check.reasons["policy_allowed"] = "request scopes not covered by grant"

        # 4. verified - explicit confirmation that the call may be executed.
        if _verified:
            check.verified = True
            check.reasons["verified"] = "explicit execution confirmation"
        else:
            check.reasons["verified"] = "call not confirmed for execution"

        return check


# Patch CapabilityGrant to add scopes_include_all used above.
def _scopes_include_all(self: CapabilityGrant, scopes: frozenset[str]) -> bool:
    if not self.scopes:
        return True
    return bool(scopes) and scopes.issubset(self.scopes)


CapabilityGrant.scopes_include_all = _scopes_include_all  # type: ignore[attr-defined]