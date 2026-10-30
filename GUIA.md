# Guía de operación

## El comando principal

```powershell
.\.venv\Scripts\python.exe -m isyco_calle.demo
```

## Regla de oro

**Nunca ejecutes una llamada real sin un número consentido, un grant firmado y
una clave de idempotencia estable.** `--allow` confirma la ejecución, pero no
concede autoridad.

## Comandos probados

### 1. Demostración offline

```powershell
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe -m isyco_calle.demo
```

Salida real (el identificador del mock cambia en cada ejecución):

```text
ISyCo CALL Bridge — golden demo
(offline mock; --real is disabled)

[request]
  objective : Confirm whether the business is open tomorrow
  target    : +15555550142

============================================================
PATH A — denied (no authority grant)
[authority] no grant present
[result]    status = rejected
[detail]    authority denied: {'technically_possible': 'capability registered', 'authorized': 'no explicit grant for caller/capability', 'verified': 'call not confirmed for execution'}
[fact]      provider touched = False

============================================================
PATH B — authorized
[authority] grant issued; verified = true
[provider]  mock
[result]    status = success
            request_id = mock_c3f81c70
            structured_output = {'ok': True}

============================================================
SUMMARY
============================================================
  denied  -> no call      (provider untouched: True)
  granted -> success via mock (mock_c3f81c70)
```

### 2. Suite offline

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Salida real:

```text
.......................................ss..................              [100%]
57 passed, 2 skipped in 0.49s
```

### 3. Comprobar configuración sin llamar

```powershell
$env:CALLE_API_KEY=$null
.\.venv\Scripts\python.exe -m isyco_calle.cli doctor
```

Salida real:

```text
{
  "command": "doctor",
  "cli": "ok",
  "config": "error: CALLE_API_KEY is not set. Get an API key from the CALL-E dashboard (https://dashboard.heycall-e.com/account/api-keys) and export it.",
  "sdk": "error: CALLE_API_KEY is not set. Get an API key from the CALL-E dashboard (https://dashboard.heycall-e.com/account/api-keys) and export it.",
  "provider": "calle",
  "base_url": "https://api.heycall-e.com",
  "env_var": "CALLE_API_KEY"
}
EXIT=1
```

### 4. Emitir un grant desde el contexto de confianza

Prerequisito: la clave privada que corresponde al trust anchor fijado en esta
versión debe haber sido provisionada fuera del repositorio por su custodio. En
esta estación de desarrollo se utilizó la ruta temporal siguiente; una copia
limpia no la crea ni puede sustituir el trust anchor.

```powershell
$private = Join-Path $env:TEMP "isyco-calle-guide-private.pem"
$grant = Join-Path $env:TEMP "isyco-calle-guide-grant-v2.json"
.\.venv\Scripts\python.exe -m isyco_calle.cli grant-issue `
  --caller demo-owner --capability phone.call `
  --expires-at 2026-09-15T00:00:00Z --scope phone:+15555550123 `
  --private-key-file $private --out $grant
```

Salida real:

```text
{
  "command": "grant-issue",
  "output": "C:\\Users\\progr\\AppData\\Local\\Temp\\isyco-calle-guide-grant-v2.json",
  "caller": "demo-owner"
}
```

La clave pública correspondiente está fijada en el paquete: el agente no puede
sustituirla. La privada usada en esta prueba está fuera del repositorio; antes
de producción debe moverse a almacenamiento protegido. Ese traslado está
**NO PROBADO** porque requiere decidir la ubicación/ACL del despliegue.

### 5. Smoke live — NO PROBADO

```powershell
$env:CALLE_API_KEY="<clave-real>"
$env:CALL_E_LIVE="1"
$env:CALL_E_TEST_PHONE="<numero-E.164-consentido>"
$env:CALL_E_TEST_IDEMPOTENCY_KEY="<clave-unica-y-estable>"
.\.venv\Scripts\python.exe -m pytest tests/test_live_smoke.py -m live -v
```

Sin credenciales, la comprobación segura produce:

```text
collected 2 items
2 skipped in 0.06s
EXIT=0
```

Con credenciales puede efectuar una llamada real. Esa variante todavía está
marcada **NO PROBADO** en este repo hasta disponer del número consentido.

## Cómo leer los estados y códigos

| Estado/código | Significado | Acción |
|---|---|---|
| `success`, 0 | Resultado demostrado | Revisar evidencia y transcript |
| `rejected`, 2 | Autoridad o confirmación denegada | No reintentar sin un grant válido |
| `not_demonstrated`, 3 | Evidencia insuficiente | Inspeccionar resultado antes de decidir |
| `failed`/`timeout`/`provider_error`, 1 | Fallo operativo | Corregir la causa; reutilizar idempotencia |
| test `skipped` | Faltó alguna puerta live | No se realizó llamada |

## Trampas

- `--allow` no reemplaza el grant firmado en operaciones reales.
- Nunca entregues la clave privada al agente o proceso que ejecuta llamadas.
- En Windows, guarda la privada y los receipts en una carpeta con ACL restringida;
  `0600` no sustituye una ACL de Windows.
- Un grant de llamada se liga a `phone:<E.164>`; uno de estado se liga a `call:<id>`.
- No cambies la clave de idempotencia al reintentar la misma llamada.
- `CALLE_BASE_URL` debe ser HTTPS; una URL vacía o HTTP se rechaza.
- El test live necesita las cuatro variables; sin ellas se omite de forma segura.
