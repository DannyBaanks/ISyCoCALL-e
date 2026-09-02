import pytest

from isyco_calle.domain.authority import (
    AuthorityDecision,
    AuthorityEvaluator,
    CapabilityGrant,
)


def test_no_grant_is_denied():
    ev = AuthorityEvaluator()
    check = ev.evaluate(caller="alice", capability="phone.call", _verified=True)
    assert check.decision() is AuthorityDecision.DENY
    assert check.technically_possible is True
    assert check.authorized is False


def test_grant_but_not_verified_is_denied():
    ev = AuthorityEvaluator()
    ev.grant(CapabilityGrant(caller="alice", capability="phone.call"))
    check = ev.evaluate(caller="alice", capability="phone.call", _verified=False)
    assert check.decision() is AuthorityDecision.DENY
    assert check.authorized is True
    assert check.policy_allowed is True
    assert check.verified is False


def test_full_allow():
    ev = AuthorityEvaluator()
    ev.grant(CapabilityGrant(caller="alice", capability="phone.call"))
    check = ev.evaluate(caller="alice", capability="phone.call", _verified=True)
    assert check.decision() is AuthorityDecision.ALLOW
    assert check.to_dict()["decision"] == "allow"


def test_axes_are_not_collapsed():
    ev = AuthorityEvaluator()
    ev.grant(CapabilityGrant(caller="alice", capability="phone.call"))
    check = ev.evaluate(caller="alice", capability="phone.call", _verified=False)
    d = check.to_dict()
    assert d["technically_possible"] is True
    assert d["authorized"] is True
    assert d["policy_allowed"] is True
    assert d["verified"] is False
    assert d["decision"] == "deny"


def test_region_scope_required_when_grant_scoped():
    ev = AuthorityEvaluator()
    ev.grant(CapabilityGrant(caller="alice", capability="phone.call", scopes=frozenset({"US"})))
    ok = ev.evaluate(caller="alice", capability="phone.call", scopes=frozenset({"US"}), _verified=True)
    assert ok.decision() is AuthorityDecision.ALLOW
    bad = ev.evaluate(caller="alice", capability="phone.call", scopes=frozenset({"MX"}), _verified=True)
    assert bad.decision() is AuthorityDecision.DENY
    assert bad.policy_allowed is False


def test_revoke():
    ev = AuthorityEvaluator()
    ev.grant(CapabilityGrant(caller="alice", capability="phone.call"))
    ev.revoke("alice", "phone.call")
    check = ev.evaluate(caller="alice", capability="phone.call", _verified=True)
    assert check.decision() is AuthorityDecision.DENY