# CALL-E Surface (verified)

Date: 2026-09-02. Source: official CALL-E documentation and a real SDK install probe.
Each claim cites its source. `[VERIFIED]` = confirmed by a live probe on this host;
`[DOC]` = from official docs/README; `[NOT_DEMONSTRATED]` = not yet proven on this host.

## What CALL-E is

CALL-E is a developer-first platform for building AI agents that place real phone
calls and return structured results: it plans, dials, holds a conversation, adapts
in real time, and returns structured data, transcript, and summary.
`[DOC]` — call-e-integrations README.

## Integration paths offered (official)

| Path | Entry | Notes |
|---|---|---|
| Skill | `npx -y skills add https://github.com/CALLE-AI/call-e-integrations --skill calle -g` | uses the local `calle` CLI |
| CLI | `npm install -g @call-e/cli` | commands: `calle auth login/status`, `calle mcp tools` |
| MCP | Streamable HTTP endpoint `https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth` | tools: `plan_call`, `run_call`, `get_call_run` |
| SDK | TypeScript `@call-e/calle`; **Python `calle-ai`** | used here |
| API | REST, base `https://api.heycall-e.com` | `POST /v1/calls`, `GET /v1/calls/{id}`, `GET /v1/calls/{id}/events`, `POST /calle/webhook` |

Source: call-e-integrations README (`[DOC]`).
**Decision: Python SDK `calle-ai`.** Matches ISyCo's Python-heavy stack, minimal deps,
local on Windows, and maps directly to the vertical slice.

## Python SDK (chosen path)

Install: `pip install calle-ai` — version installed: **0.7.0** `[VERIFIED]`
Dependencies: `attrs`, `httpx` `[VERIFIED]`

```
from calle import CalleClient
client = CalleClient(api_key=os.environ["CALLE_API_KEY"])   # or CALLE_BASE_URL / timeout
call = client.calls.create_and_wait(task=..., result_schema={...})
```

Real signatures (inspected on installed SDK, `[VERIFIED]`):

- `CalleClient(*, api_key: str, base_url: str = 'https://api.heycall-e.com', timeout: float = 30.0, http_client=None)`
- `calls.create(*, task, recipient=None, recipients=None, result_schema=None, recipient_result_schema=None, metadata=None, webhook_url=None, idempotency_key=None) -> dict`
- `calls.create_and_wait(**kwargs) -> dict` — `create()` then `wait_for_result(call["id"])`
- `calls.get(call_id) -> dict`
- `calls.list_events(call_id, *, cursor=None, limit=None) -> dict`
- `calls.wait_for_result(call_id, *, interval_seconds=2.0, timeout_seconds=600.0) -> dict`

## Authentication

- Env var: **`CALLE_API_KEY`** `[DOC]`
- Key format: `calle_live_key` (placeholder in docs) `[DOC]`
- Dashboard: `https://dashboard.heycall-e.com/account/api-keys` `[DOC]`
- New accounts get 20 free calls `[DOC]`
- Additional calls via request form `[DOC]`

## Result / lifecycle

Terminal statuses returned by `wait_for_result`: **`completed`, `failed`, `canceled`** `[VERIFIED]`
(same set from the docs' "Reliable terminal state workflow").

On local timeout `wait_for_result` raises **`CalleTimeoutError`** `[VERIFIED]`.

Result fields (official README response example `[DOC]`):
`status`, `task_completed`, `completion_confidence{score,label}`, `evidence[]`,
`structured_result`, `recipients[].structured_result`,
`recipients[].attempts[].transcript_turns[] {offset_seconds, speaker, text}`.

Note: `started_at` / `finished_at` are NOT confirmed by docs as returned fields; the
adapter reads them defensively (stays `None` when absent) rather than inventing them.

## Error taxonomy (installed SDK `[VERIFIED]`)

`CalleAPIError(code, status_code, message, details)`,
`CalleAuthenticationError(CalleAPIError)`,
`CalleConnectionError`, `CalleRateLimitError`, `CalleTimeoutError`, `CalleWebhookSignatureError`.

## Request shape for our capability

`create()` accepts `task` (natural-language goal), `recipient={phones:[...], region, locale}`,
`result_schema` (JSON Schema for structured output), `metadata`, `idempotency_key`.

## Regions / languages (official `[DOC]`)

`US, SG, MY, IN, AE, AU, CA, GB, VN, DE, JP, FR, MX, BR, ID, PH, KE, NL, PL, BD, NG, OM,
TH, NA, CM, MZ, SA, FI, UA, LK, BW, PK, TR, HN, ES, TW, ZA, EG, GH, IL, IE, TN`.
`Local` line for some; `International` for others (mainly for testing) — see README table.

## Limits / safety (official `[DOC]`)

Rate limits, concurrency controls, number governance, blocklists, kill switches,
redacted logs, audit trails. No exact numeric limits published in the surface docs we read.

## NOT_DEMONSTRATED on this host

- Real outbound call (`REAL_CALL = NOT_DEMONSTRATED` — no `CALLE_API_KEY` here).
- OAuth / MCP / broker login flows (not needed for the SDK path).
- Exact live response shape (derived from official README example, not observed).

## Sources

- Installation guide: https://open.heycall-e.com/document/mcp-archive/CALL-E-installation-guide.md
- Integrations repo (README, API/SDK/MCP, regions, telemetry): https://github.com/CALLE-AI/call-e-integrations
- Docs / API reference: https://docs.heycall-e.com/
- Dashboard (API keys): https://dashboard.heycall-e.com/account/api-keys
- Hackathon: https://call-e.devpost.com/
- Installed SDK probe: `evidence/probe_sdk_surface_20260902.txt`