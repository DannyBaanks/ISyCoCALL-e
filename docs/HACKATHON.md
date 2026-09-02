# Hackathon — ISyCo CALL Bridge

Submitted to: **CALL-E: Your Code Is Calling** (https://call-e.devpost.com/).

## Problem

A phone call is the last frontier an agent cannot cross by itself. A structured
pipeline (webhook → API → database) can confirm, schedule, and verify nearly anything —
until the *only* way to reach a person or business is a real phone call. ISyCo's
civilization/agent substrate reasons about intents and capabilities, but it has no way to
turn a phone interaction into a structured, consumable result. Businesses are often
unreachable except by phone (a shop with no booking API, a supplier who only takes calls,
an appointment line that does not expose a webhook). The gap: **the agent knows *what* to
ask but cannot *dial***, and anything it cannot reach by API it cannot act on.

## Why CALL-E (not decorative)

- CALL-E turns a natural-language goal into a real placed call, holds a conversation that
  adapts, and returns a **schema-validated structured result** plus transcript and summary.
- That structured result is what ISyCo's reasoner can consume. Without it, a "call" is just
  a side effect with no data; with it, a call becomes a first-class capability output.
- It is genuinely hard to hand-roll: number governance, voicemail/screening, IVR navigation,
  hold/silence handling, and result extraction are non-trivial. CALL-E already solves them.

## Architecture (path of a request)

```
structured request {action: phone.call, objective, target.phone}
      |
      v
ISyCo input contract          (isyco_calle/domain/contract.py)
      |
      v
phone.call capability         (isyco_calle/capabilities/phone_call.py)
      |  authority gate: technically_possible + authorized + policy_allowed + verified
      v
CALL-E adapter                (isyco_calle/providers/callee.py) wraps calle-ai SDK
      |  client.calls.create_and_wait(task, recipient, result_schema, ...)
      v
real CALL-E outbound call
      v
structured result             (isyco_calle/domain/result.py)
  success | failed | rejected | timeout | provider_error | not_demonstrated
      + request_id, provider, structured_output, transcript, evidence
      v
caller
```

The core principle enforced on the path: **capability != authority** — a call only happens
when every authority axis is granted (see `docs/AUTHORITY_MODEL.md`).

## What existed before (reused from ISyCo)

ISyCo is a research monorepo with an established contract discipline. We reused:
- The **capability/authority separation** idea: ISyCo already distinguishes "engine ≠ host ≠
  bridge" and treats capabilities as explicit, gated operations. The four-axis authority
  model (`docs/AUTHORITY_MODEL.md`) is a direct adaptation of that discipline.
- The **evidence-before-narrative** rule (AGENTS.md §6): every claim here is backed by a
  probe, a test, or official docs; unsupported claims are marked `NOT_DEMONSTRATED`.
- The **frozen-contract / normalized-result** habit: inputs are validated at the boundary and
  providers are replaceable behind a seam, mirroring ISyCo's adapter pattern.
- Python-first, minimal-dependency, Windows-local execution conventions.

## What was built for CALL-E (new)

- `isyco_calle/domain/contract.py` — `PhoneCallRequest` + input contract (`phone.call`).
- `isyco_calle/domain/result.py` — normalized `PhoneCallResult` with 6-status outcome model.
- `isyco_calle/domain/authority.py` — the 4-axis authority evaluator + grant model.
- `isyco_calle/capabilities/phone_call.py` — the `phone.call` capability gate.
- `isyco_calle/providers/callee.py` — the real CALL-E adapter over the `calle-ai` SDK
  (with a transcript extractor and a robust result mapping).
- `isyco_calle/providers/mock.py` — in-memory mock for tests only.
- `isyco_calle/cli.py` — `isyco-call doctor / call / status` minimal surface.
- `isyco_calle/config.py` + `.env.example` — secure `CALLE_API_KEY` config.
- `tests/` — unit + mock-adapter tests (26 pass) + LIVE-marked smoke tests.
- `docs/CALL_E_SURFACE.md`, `docs/AUTHORITY_MODEL.md`, `evidence/`.

## Demo path (~3 min)

1. `isyco-call doctor` — shows config/SDK wiring fail-closed when no key (10s).
2. Run the real vertical slice: `isyco-call call --to +1... --objective "Confirm whether the
   business is open tomorrow" --allow` → CALL-E places a real call and returns a structured
   `success` result with `structured_output`, `transcript`, and `evidence` (≤2 min).
3. `isyco-call status <call_id>` — read a result by id.
4. Safety moment: show that the same request **without** `--allow` returns
   `status=rejected` and no call is placed (capability != authority).

## Status (honest)

| Item | Status |
|---|---|
| Contract/capability/result/authority | implemented + tested |
| CALL-E adapter (real SDK wiring) | implemented (code + installed SDK) |
| CLI (doctor/call/status) | implemented + tested (mock) |
| Tests | 26 pass (2 LIVE skipped) |
| **Real outbound call** | **NOT_DEMONSTRATED** (no `CALLE_API_KEY` on this host) |

The integration is built and wired; the only missing piece is running it with live
credentials, which is a config step, not a code one.