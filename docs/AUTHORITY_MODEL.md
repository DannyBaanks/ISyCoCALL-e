# Authority Model

Goal: guarantee that **`intent == authority` cannot hold**. A caller never obtains the
power to place a phone call merely by existing. The capability must be explicitly
granted, and a call may only execute when every axis is satisfied.

## The core principle: capability != authority

- **Capability** = an operation ISyCo can perform (`phone.call`). It is *available*, not *granted*.
- **Authority** = the *permission* for a specific caller to invoke it right now.

We separate them so that "the system can call" never implies "this request may call".

## The four axes

A single boolean hides too much (a denied call can be denied for four different reasons).
We evaluate each request along four independent axes and require all four:

| Axis | Question | Source of truth (seam) |
|---|---|---|
| `technically_possible` | Is the capability registered and callable by this caller type? | Capability registry |
| `authorized` | Does the caller hold an explicit grant for the capability? | Grant store (`CapabilityGrant`) |
| `policy_allowed` | Is the grant in force and do the request parameters/scopes comply? | Policy + scopes (`region`, etc.) |
| `verified` | Is the operation explicitly confirmed for execution? | Explicit confirmation (human / issuing context) |

A call executes **only** when all four are true. See `isyco_calle/domain/authority.py`
(`AuthorityEvaluator.evaluate`, `AuthorityDecision`).

## Grant model

A grant is explicit and minimal:

```python
CapabilityGrant(caller="alice", capability="phone.call", policy="default",
                scopes=frozenset({"US"}), expires_at=None)
```

- Grant is keyed by `(caller, capability)` — a caller must be *named* and the *specific*
  capability must be named.
- `scopes` restrict what the grant covers (e.g. only `US` region). Empty set = no restriction.
- `expires_at` is honored by the policy axis (future work; the contract seam is present).
- `AuthorityEvaluator.grant(...)` / `.revoke(...)` / `.evaluate(...)`.

## Decision table

| technically_possible | authorized | policy_allowed | verified | decision |
|---|---|---|---|---|
| false | any | any | any | deny |
| true | false | any | any | deny |
| true | true | false | any | deny |
| true | true | true | false | deny |
| true | true | true | true | **allow** |

## Where the boundary is enforced

`isyco_calle/capabilities/phone_call.py` (`PhoneCallCapability.call`):

1. Validate the input contract.
2. `AuthorityEvaluator.evaluate(...)` → if `decision != ALLOW`, return
   `status=rejected` **without touching the provider**.
3. Only on ALLOW does it dispatch to the provider.

Verified in tests (`tests/test_authority.py`, `tests/test_provider_mock.py`): a caller
with no grant, or an unconfirmed request, reaches the provider **zero** times.

## How a caller is supposed to get a grant

This repo ships a **minimal contract**, not a policy engine. In production the four axes
plug into real stores:

- `authorized` ← an identity/IAM grant store
- `policy_allowed` ← a policy source (region allow-lists, quiet hours, budgets)
- `verified` ← a human-in-the-loop or issued-context confirmation (e.g. a CLI `--allow`,
  an approval ticket, a workflow step)

The CLI demonstrates the seams: `isyco-call call --allow` is the `verified` confirmation;
`--region US` feeds the scopes axis; a named `--caller` is required for the grant.

## Scope

This is intentionally small. It establishes the contract that prevents
`intent == authority` and leaves room for a real policy engine behind the seams.