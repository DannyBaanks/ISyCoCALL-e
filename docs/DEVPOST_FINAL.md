# DEVPOST_FINAL — ISyCo CALL Bridge

Copy-ready text for the Devpost submission form. Do not send this version if the dates
here don’t match; update with your real email, real PR link, and public demo URL.

## NAME
ISyCo CALL Bridge

## TAGLINE
“When there is no API, the phone becomes one — without giving the agent unlimited
authority.”

## ONE-SENTENCE
ISyCo CALL Bridge lets an automated workflow safely resolve real-world tasks that
have no API by placing authority-gated phone calls and returning normalized,
actionable outcomes.

## PRIMARY USE CASE
Workflow and back-office automation.

## WHAT IT DOES
ISyCo CALL Bridge gives an existing agent system a well-defined phone capability.
A request starts as a structured phone call contract (`action`, `objective`,
`target`, `result_schema`) and exits as a capability that only runs when the caller
is explicitly authorized. The vertical slice uses CALL-E to place the real outbound
call; the result comes back as a normalized, structured record your agent can read.

## WHY IT MATTERS
Your workflow can correctly handle APIs until one cannot. When an interaction only
exists as a phone number, agents without boundaries fail (or silently pretend it
worked). This project does not pretend, it executes with science:

- Capability (`phone.call`) and **authority** are separate
- An unauthorized caller never reaches a real phone.
- The result is normalized into a shape an agent can act on
- Statuses distinguish provider failures (wrap-around, NOT-AVAILABLE,
  callee disconnected etc.)

## HOW BUILT
- Authority model: 4-axis (technically_possible, authorized, policy_allowed,
  verified). Explicit dual-dial double-dialing is prohibited.
- Provider adapter wraps the CALL-E `calle-ai` Python SDK (official).
- The CLI is minimal: `doctor`, `call`, `status`. Fully debuggable from PowerShell
- Tests, evidence, and clides with precise outputs (sha256-hashed).

## KEY LEARNING / WHAT WAS HARD
Taking the time to learn CALL-E's actual API/CLI surface—and finding two authentic
production issues in the process while doing so. The discovery of #103 (new-user
account provisioning) because we validated claims instead of assuming a signup worked,
and surfaced as forensics #105 (carrier-level outcome that gets lumped in with
user "missing" basics).

## WHAT WAS BUILT FOR THE HACKATHON
- The full vertical slice (contract → capability → provider → result)
- The authority model and CLI
- A real CALL-E provider adapter (using the official SDK)
- Defensive unit tests (28) :: -- live_walkthrough on anthropic dev post
- Documentation: `docs/HACKATHON.md`, `docs/AUTHORITY_MODEL.md`, evidence backups

## WHAT WAS BUILT IN-HOUSE (BEFORE)
( the ISyCo discipline of capabilities/authority; the monorepo approach, and
easy observability the project carries forward.)

## PR III issue intake link (required)
- PR #104: https://github.com/CALLE-AI/call-e-integrations/pull/104

## CALL-E ACCOUNT EMAIL
<fill-in-with-your-email>

## PUBLIC DEMO LINK (3min video)
<fill-in-your-youtube/vimeo-link>

## TESTING INSTRUCTIONS
See: `docs/TESTING_INSTRUCTIONS.md` (local mock, offline; no CALL-E credentials
required). Live demo requires a `CALLE_API_KEY`. If you have questions,
please ask.
