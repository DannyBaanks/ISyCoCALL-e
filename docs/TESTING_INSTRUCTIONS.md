# TESTING INSTRUCTIONS — ISyCo CALL Bridge

Live-testable (actually dials) requires real CALL-E credentials. Tests without them
are fully mockable. Mock paths are never presented as real.

## Option A: offline / mock (no CALL-E needed)

```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
# mock only — no network, no CALL-E
.\.venv\Scripts\python.exe -m isyco_calle.cli doctor
.\.venv\Scripts\python.exe -m isyco_calle.cli call \
    --to +15555550123 --objective "confirm a business is open tomorrow" --mock
```

Expected:
- `doctor` prints config status (_apikey_, SDK path).
- call prints `status: rejected` when `--allow` is omitted (authority gate),
- or `status: success` with `provider: mock` when `--mock` and `--allow` used.

Or run tests:

```bash
.\.venv\Scripts\python.exe -m pytest -q
# -> 28 passed (2 skipped LIVE)
```

## Option B: live smoke (requires CALLE_API_KEY, one call)

```bash
$env:CALLE_API_KEY="<live key>"
python -m pytest tests/test_live_smoke.py -m live -v
```

Want a deterministic outcome? The result shows a real call transcript, but local
reality (region/carrier/route) may make the call not ring at all — still a valid
structured result as long as the status is not pretending.
