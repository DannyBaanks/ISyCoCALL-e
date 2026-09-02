# Awesome Phone Call Agents — contribution draft

Status: DRAFT. Do NOT open a PR until a real CALL-E call is demonstrated
(`REAL_CALL = NOT_DEMONSTRATED` today). Submission target repo:
https://github.com/CALLE-AI/awesome-phone-call-agents

Contribution area: **App** (`apps/python/...`), consistent with existing entries like
`apps/python/appointment-confirm`.

## Entry (README list)

- [ISyCo CALL Bridge](https://github.com/<you>/isyco-calle) — Capability-gated CALL-E
  adapter that turns a structured `phone.call` request into a real call and a normalized
  structured result, enforcing a four-axis authority boundary so `intent` never equals
  `authority`.

## Proposed folder

```
apps/python/isyco-call-bridge/
├── README.md
├── isyco_calle/
├── tests/
└── docs/
```

## Name

`ISyCo CALL Bridge`

## Short description

A minimal, authority-gated CALL-E vertical slice: `phone.call` capability → `calle-ai`
adapter → real CALL-E call → normalized structured result (success/failed/rejected/timeout/
provider_error/not_demonstrated). Emphasizes the `capability != authority` boundary.

## Use case

Any agent that needs a real phone interaction where no API exists — confirming a business is
open, verifying a listing, reaching a supplier who only answers calls — and must return a
structured, consumable result to the calling system while requiring an explicit grant to dial.

## CALL-E surface used

- Python SDK `calle-ai` (`CalleClient.calls.create_and_wait(task, recipient, result_schema, ...)`)
- Env auth via `CALLE_API_KEY`
- Result mapping: `status`, `task_completed`, `completion_confidence`, `structured_result`,
  `evidence`, `recipients[].attempts[].transcript_turns[]`

## Run instructions

```
py -m venv .venv
.venv\Scripts\python -m pip install -e .
export CALLE_API_KEY=calle_live_key          # PowerShell: $env:CALLE_API_KEY="..."
.venv\Scripts\python -m isyco_calle.cli doctor
.venv\Scripts\python -m isyco_calle.cli call --to +15555550123 \
    --objective "Confirm whether the business is open tomorrow" --allow
.venv\Scripts\python -m isyco_calle.cli status <call_id>
.venv\Scripts\python -m pytest -q
```

Tests: unit + mock adapter run offline; LIVE smoke tests are skipped unless
`CALLE_API_KEY` and `CALL_E_LIVE=1` are set. Safety: no call is placed without `--allow`
(the `verified` axis) and an explicit grant.

## Compliance notes

- Consent / disclosure, E.164 phone handling, credential boundaries per the repository's
  safety guidance.
- Fail-closed dispositions: unknown/unreached outcomes map to `not_demonstrated` /
  `rejected`, never to `success`.
- No call without explicit authority; mock paths never presented as live evidence.

## Blockers to opening the PR

- Place and verify at least one real call with live credentials.
- Choose a public repo URL for the entry link.
- Run `python3 scripts/validate_repository.py` on the target repo.