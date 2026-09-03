# SUBMISSION CHECKLIST — ISyCo CALL Bridge

Prepares you for the Devpost submission form for the CALL-E hackathon.

- [ ] **Testing instructions** clear and tested: both offline/mock and live versions.
- [ ] **PR to calle repo** is open and useful. (We currently have https://github.com/CALLE-AI/call-e-integrations/pull/104 — docs improvement #104, and issue #105 for outcome semantics.)
- [ ] **Public problem remake** (3 minute YouTube/Vimeo). Does it demonstrate?
  * caller has capability-gated authority
  * real CALL-E being hit at runtime
  * results normalized into structured output
  * clear before/after (or deny/pass)
- [ ] **CALL-E account email** freehand; fill in the email of the caller/user here.
- [ ] **Condensed text** for "problem solved" and "why it matters", answered between 75 and 150 characters (yes, only that much), hypothesis, hypothesis-driven evidence (done)

## what you built (already)

- Vertical slice manner technological: request → capability → provider → result
- Authority model (4 axes, denied means never dialed)
- Provider adapter against puntest `calle-ai` SDK
- Minimal CLI (doctor, call, status)
- Test for the foo boss (28 PASS)

## What is still needed (optional but recommended)

- A real live call placed (we have evidence from yesterday of a real attempt in
  rescue but not from within the product itself) — uncomment a line from
  `tests/test_live_smoke.py` with your real `CALLE_API_KEY` only if you will never
  share an API key with anyone. Make sure it exists in the test output only.

## reminder

- Do not fake your having a real call (sn show achieved records, then say
  explicitly if call fallback real issues.
- Don't call numbers without direct user consent/authority.