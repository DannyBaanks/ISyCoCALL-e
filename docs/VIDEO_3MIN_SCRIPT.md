# Video Script — 3 Minutes, ISyCo CALL Bridge

Title card: **ISyCo CALL Bridge — “When there is no API, the phone becomes one.
Without giving the agent unlimited authority.”**

(Don’t show this script to judges; show them what the commands print and so on.)
(Time references are for the minimal product demo, not trying ours.)

---

### 0:00 – 0:25 · Problem

Screen, no narration.

Show a workflow diagram: agent → API → API → **×** → phone number only.

VO: “Agents are good at JSON, webhooks, and APIs. But some business tasks only live behind a phone number.”

Screen: `README.md` first screen (the diagram with the four authority axes).

Point to line: `intent → capability → CALL-E → phone → structured result`.

---

### 0:25 – 1:05 · Authority path

Terminal. `isyco-call doctor`.

The screen shows four gates: `technically_possible`, `authorized`, `policy_allowed`, `verified`.

VO: “Every call has to pass four gates. Not a boolean. If any gate fails, the call doesn’t happen.”

Screen: `isyco-call call --to +1… --objective “Confirm business is open tomorrow”` (no --allow).

Output highlights:
```
"status": "rejected"
…
"reasons": { "verified": "call not confirmed for execution" }
```

---

### 1:05 – 2:00 · Authorized path

Same input. This time they type:

```bash
isyco-call call --to +1... --objective "Confirm business is open tomorrow" --allow
```

The screen highlights:
```
authority check → ALLOW
provider → CALL-E → real request
```

VO: “Same request, but with explicit verification. Now the call happens for real—through CALL-E, which actually dials.”

Briefly show: `calle auth status` → status usable.

(B-roll: planning screenshot or the `#!` on the phone that rings on your desk.)

⚠️ Don’t show policies or contrived demo numbers. Use a Danny-controlled number and
say “my number”.

---

### 2:00 – 2:45 · Result

Output: normalized result JSON.

Show the fields:
- `request_id: call_...` (real provider-assigned ID will depend on the state
- raw result of recordings)
- `provider: calle`
- `status: success` (with fields filled by evidence) or `no-answer` with a raw evidence
- Call result durations/confidence summaries.

Show the same example as in the README (the vertical demo path: “open tomorrow?”
returns yes/no evidence).

VO: “The agent gets a structured result they can act on. Not speculation—evidence.”

---

### 2:45 – 3:00 · Close

Screen: README tagline + PR link to #104.

Text slide:
**ISyCo CALL Bridge — for the CALL-E hackathon. How does it work? Try it.**

VO: “We built a phone fallback for real work. It respects authority, and it’s here.”

---

### Production notes

- Use a real CALL-E number for confirmed ingestion; know the status.
- Do not place real calls in advanced demoing. Avoid mock videos claiming to be live. Liveness is overcapable at this stage.
- All evidence references should be real and locally produced (docs/, evidence/, logs).
- Method, not garnish. Keep the demo independent: no clone of another agent left ambiguous.

---