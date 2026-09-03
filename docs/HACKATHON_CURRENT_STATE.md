# Current State — 2026-09-03 (post-forensics, pre-submission)

This is the honest snapshot of what exists today. Nothing here is invented.

## Tests

- `python -m pytest -q` → **28 passed, 2 skipped** (offline, live skipped without creds)
- `tests/test_live_smoke.py` → 2 tests marked `LIVE`, skipped without `CALLE_API_KEY`
- `providers/mock.py` → **mock only, never passed as live**

## Auth

- `CALLE_API_KEY` → **NOT SET** on this host (dashboard key needed for a REAL call)
- `auth login` (CLI) live-tested earlier today on this host Windows: status=usable (token valid until 2029-05) → **cached as auth evidence for the calle CLI**
- `calle auth status` on the rescue dequeue → `usable: true` as of 2026-09-03 (ordered from the Windows session to the demo later)

## Real outbound calls TODAY (2026-09-02/03 via `calle` CLI from the same number as Danny)

| run_id | status | hangup_type | dur | owner saw ring? |
|---|---|---|---|---|
| LYI-oVFn9FUA6doPVhTsLA | NO ANSWER | ByCallee | 0s | NO |
| 1BiD4vn4pxCOwowRW7VKMw | NO ANSWER | ByCallee | 0s | NO |
| nVI50x8GEIBpS7-yF1hEvQ | NO ANSWER | ByCallee | 0s | NO |

**None rang** → outcome semantics documented in issue #105 (filed today, as a
`UPSTREAM` issue against CALL-E, 3 independent confirmations).

The real outbound call **reached the provider** — but the carrier/region behavior is
NOT_DEMONSTRATED as actually ringing a handset in MX. What we can do in a demo is
show the flow end-to-end and report the truthful result (caller got placed, phone
didn't ring), not claim victory.

## What the hackathon submission **should NOT claim**

- Real outbound call completed: NO. (All three live attempts were NOT_DEMONSTRATED).
- Got it working end-to-end, so a production-ready call. NO. First-off-ring, but the
  substantive outcome mission is not resolved.
- The fast auth fix (#103) already resolved. It's now in triage by maintainers after the PR (#104).

## Evidence lives in

- `CALL-E-AUTH-RESCUE_HACKATHON/` (adjacent) — has the live auth session, the
  calls, the `evidence/auth-rescue/*.json` files, and the `NO ANSWER` issue with 3
  hashes.
- `docs/HACKATHON.md` — narrative for the hackathon submission (this is what to refine).
- `evidence/` — CLI slice probe + SDK surface verification (already dated 2026-09-02).

## What the hackathon submission **CAN claim**

- Architecture finalized (input contract → capability → provider → result).
- Authority model real: DENIED without grant (2-axis result proven).
- Provider normalization real: surfaces CallResult with 6 statuses and carriers raw.
- CALL-E reference integration real: `calle-ai` SDK really installed, really called
- Locals agents cloned to Linux (Steam Deck) and ALSO ran there (evidence in auth repo).
- Two public PRs filed (docs #104, call-outcome semantics #105) — the first-quality
  evaluation step of a hackathon submission is to be upstream-friendly.

The repo is **not marketing-ready** — it documents the work honestly.