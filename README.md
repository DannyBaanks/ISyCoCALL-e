# ISyCo CALL Bridge

Capability-gated phone calls for ISyCo via CALL-E.

```
intent -> capability -> CALL-E -> phone interaction -> structured result -> caller
```

## What

A minimal, real vertical slice that lets an ISyCo agent turn a structured request
(`phone.call`) into a real outbound phone call through CALL-E, and receive a normalized
structured result back.

## Why

A phone call is often the only way to reach a person or business (no booking API, a
supplier who only takes calls, an appointment line without a webhook). CALL-E turns a goal
into a real call and returns a schema-validated result an agent can actually act on.

## Architecture

```
structured request -> input contract -> phone.call capability (authority gate)
    -> CALL-E adapter (calle-ai SDK) -> real CALL-E call
    -> structured result (6-status outcome) -> caller
```

Core principle: **capability != authority**. A call only executes when four axes are granted:
`technically_possible`, `authorized`, `policy_allowed`, `verified`
(see `docs/AUTHORITY_MODEL.md`).

```
isyco_calle/
  domain/contract.py     PhoneCallRequest + input contract
  domain/result.py       PhoneCallResult + 6-status outcome model
  domain/authority.py    4-axis authority evaluator + grants
  capabilities/phone_call.py   the phone.call capability gate
  providers/callee.py    real CALL-E adapter over calle-ai SDK
  providers/mock.py      in-memory mock (tests only)
  cli.py                 isyco-call doctor/call/status
  config.py              secure env config (CALLE_API_KEY)
```

## Quickstart

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
Copy-Item .env.example .env          # then set CALLE_API_KEY (or export it)
.\.venv\Scripts\python.exe -m isyco_calle.cli doctor
```

## Configuration

Secrets come only from environment variables (no hardcoded tokens):

| Variable | Required | Purpose |
|---|---|---|
| `CALLE_API_KEY` | yes | CALL-E API key (dashboard.heycall-e.com/account/api-keys) |
| `CALLE_BASE_URL` | no | default `https://api.heycall-e.com` |
| `CALLE_TIMEOUT` | no | SDK timeout, default 120s |
| `ISYCO_CALL_DEFAULT_CALLER` | no | default caller identity for CLI authority checks |

Missing key → clear error and fail-closed (`doctor` exit 1).

## Run

```powershell
# check config + SDK wiring (no call placed)
.\.venv\Scripts\python.exe -m isyco_calle.cli doctor

# place a call (authority-gated; --allow is the "verified" confirmation)
.\.venv\Scripts\python.exe -m isyco_calle.cli call --to +12025550123 `
    --objective "Confirm whether a business is open tomorrow" --allow

# read a result by id
.\.venv\Scripts\python.exe -m isyco_calle.cli status <call_id>
```

Call without `--allow` returns `rejected` and places no call (capability != authority).
`--mock` uses the in-memory mock provider for offline testing.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q
```

- Unit: contract, result, authority (offline).
- Adapter: explicit mock provider (offline).
- Live smoke: `tests/test_live_smoke.py`, marked `LIVE`, skipped unless `CALLE_API_KEY`
  is set (and `CALL_E_LIVE=1` for the real-call test). A mock is never presented as live.

## Evidence

`evidence/` holds probe outputs (SDK surface, CLI slice). Hashes/artifacts added as real
calls are run. No secrets are stored.

## Hackathon

Built for the CALL-E hackathon (call-e.devpost.com). Details in `docs/HACKATHON.md`.

## Status

| Item | Status |
|---|---|
| Contract / capability / result / authority | implemented + tested |
| CALL-E adapter (real SDK wiring) | implemented + tested (SDK installed) |
| CLI (doctor/call/status) | implemented + tested |
| Tests | 26 pass, 2 LIVE skipped |
| **Real outbound call** | **NOT_DEMONSTRATED** (no `CALLE_API_KEY` on this host) |
| Awesome-phone-call-agents PR | planned (not opened) — see `docs/AWESOME_PHONE_CALL_AGENTS.md` |