# ISyCo CALL Bridge

When there is no API, the phone becomes one — **without giving the agent unlimited
authority.**

## What

A minimal, real fallback for agent workflows. When an interaction has no API and the
agent can't proceed, this turns a structured request (`phone.call`) into a real
outbound phone call through CALL-E — then normalizes the result so an agent can
consume it.

```
intent -> capability -> CALL-E -> phone interaction -> structured result -> caller
```

Core principle: **capability != authority**. A call only happens when all four
authority gates pass (`technically_possible`, `authorized`, `policy_allowed`,
`verified`).

## Golden demo (one command)

```powershell
.\.venv\Scripts\python.exe -m isyco_calle.demo
```

This shows both paths in ~5 seconds:

- **PATH A (denied)**: the request enters, no caller grant exists, result is
  `rejected` and **no call is placed** (provider untouched).
- **PATH B (authorized)**: an explicit grant is issued at runtime (in this demo,
  verified confirmation is satisfied), a real call is requested through the
  CALL-E provider, and the normalized result is returned.

## Architecture

```
structured request {action: phone.call, objective, target.phone}
      |
      v
PhoneCallRequest contract (isyco_calle/domain/contract.py)
      |
      v
phone.call capability gate (isyco_calle/capabilities/phone_call.py)
      |  authority: technically_possible + authorized + policy_allowed + verified
      v
CALL-E provider adapter (isyco_calle/providers/callee.py)
      |  wraps the official calle-ai SDK (real, not a stub)
      v
real CALL-E call (real outbound, real result)
      v
PhoneCallResult (isyco_calle/domain/result.py)
  success | failed | rejected | timeout | provider_error | not_demonstrated
      + request_id, provider, transcript, evidence, summary
```

## Run it

```powershell
# setup (silent)
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .

# doctor (no call placed — gate check)
.\.venv\Scripts\python.exe -m isyco_calle.cli doctor

# place a call (authority-gated; real network only with --real + CALLE_API_KEY)
.\.venv\Scripts\python.exe -m isyco_calle.cli call --to +12025550123 \
    --objective "Confirm whether a business can attend tomorrow" --allow
```

Note: calls without `--allow` return `rejected` and place no call.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

- 28 unit tests pass (mock only, no live dependency).
- `tests/test_live_smoke.py` is `LIVE`-marked and skips without `CALLE_API_KEY`.
- A mock provider exists in `providers/mock.py` and *is never presented as a live
  call#.

## Evidence

The `evidence/` directory holds probe outputs and per-call run JSON captures (SHA-256
hashed). No secrets are stored. For full forensics on how the outcome semantics
of real calls (why some outcome statuses are misleading), see `../CALL-E-AUTH-
RESCUE-HACKATHON/` — separate repo with the full workout and hash chains (linux
+ windows runs, exact call IDs).

## Hackathon

Built for the **CALL-E: Your Code Is Calling** hackathon (call-e.devpost.com).
Our issue and PR are tracked in `docs/SUBMISSION_CHECKLIST.md`.