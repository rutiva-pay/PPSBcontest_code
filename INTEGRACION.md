# Guía de integración — Rutiva API

Esta guía explica cómo aceptar pagos C2P (Customer-to-Payment) en tu sitio o aplicación usando la API de Rutiva.

> **Base URL producción**: `https://rutiva-api.onrender.com`
> **Documentación interactiva (Swagger UI)**: `https://rutiva-api.onrender.com/docs`

---

## 1. Conceptos clave

| Concepto | Descripción |
|---|---|
| `payment_intent` | Objeto que representa un pago en curso. Tiene un ciclo de vida: `created → succeeded / failed / canceled`. |
| `sk_xxx` | **Secret key**. Se usa en tu **backend** para crear intents. **Nunca exponer al navegador.** |
| `client_secret` | Token de un solo uso vinculado a un `payment_intent`. Se entrega al navegador para confirmar el pago sin exponer `sk_`. |
| `whsec_xxx` | **Signing secret** del webhook. Se usa para verificar que las notificaciones vienen de Rutiva. |
| OTP | Código que el banco del cliente le envía por SMS. El cliente lo escribe en tu UI para confirmar. |

### Flujo recomendado (Stripe-style)

```
┌──────────┐  1. crear intent     ┌─────────────┐  2. crear intent (sk_)  ┌────────────┐
│ Cliente  │ ───────────────────▶ │ Tu backend  │ ──────────────────────▶ │ Rutiva API │
│ (browser)│                      │             │                         │            │
│          │ ◀─── client_secret ─ │             │ ◀─── client_secret ──── │            │
│          │                      └─────────────┘                         │            │
│          │  3. confirm con OTP + client_secret                          │            │
│          │ ─────────────────────────────────────────────────────────▶  │            │
│          │ ◀─── payment_intent (succeeded / failed) ───────────────────│            │
└──────────┘                                                              └────────────┘
```

El **backend** del comerciante guarda `sk_xxx` y crea intents. El **navegador** solo recibe el `client_secret` y confirma el pago. La `sk_` jamás toca el frontend.

---

## 2. Obtener credenciales

Durante la fase MVP, las credenciales se entregan manualmente. Solicita a Rutiva:

- `sk_test_...` o `sk_live_...` — tu API key.
- `whsec_...` — signing secret de webhooks (al registrar tu endpoint).

**Guarda `sk_` en variables de entorno**, jamás en el código fuente ni en el repo:

```bash
RUTIVA_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxxx
RUTIVA_BASE_URL=https://rutiva-api.onrender.com
```

---

## 3. Listar bancos soportados (público)

Para poblar un dropdown de "banco del cliente" en tu UI. **No requiere autenticación**, CORS abierto.

```bash
curl https://rutiva-api.onrender.com/v1/banks
```

```json
{
  "object": "list",
  "data": [
    { "code": "0114", "name": "Bancaribe" },
    { "code": "0191", "name": "BNC" },
    { "code": "0105", "name": "Mercantil" },
    { "code": "0102", "name": "Banco de Venezuela" },
    { "code": "0108", "name": "Provincial" }
  ]
}
```

Frontend (JS):

```js
const res = await fetch("https://rutiva-api.onrender.com/v1/banks");
const { data: banks } = await res.json();
// renderizar <select>
```

---

## 4. Crear payment_intent (backend, `sk_`)

`POST /v1/payments`

**Headers:**
```
Authorization: Bearer sk_live_xxxxxxxx
Content-Type: application/json
Idempotency-Key: <opcional, único por request lógico>
```

**Body:**
```json
{
  "amount": 50000,
  "currency": "VES",
  "customer_phone": "04141234567",
  "customer_id_document": "V12345678",
  "customer_bank_code": "0114"
}
```

| Campo | Tipo | Validación |
|---|---|---|
| `amount` | int | Céntimos. ≥ 1, ≤ 100_000_000_000 (mil millones). |
| `currency` | string | `"VES"` o `"USD"`. |
| `customer_phone` | string | Formato `04XXXXXXXXX` (11 dígitos). |
| `customer_id_document` | string | `V/E/J/G/P` + 6-9 dígitos. Se normaliza a mayúsculas. |
| `customer_bank_code` | string | Código de 4 dígitos. Debe estar en `/v1/banks`. |

**Respuesta `201 Created`:**

```json
{
  "id": "8d3a...uuid",
  "external_id": "pi_abc123",
  "status": "created",
  "amount_cents": 50000,
  "currency": "VES",
  "client_secret": "pi_abc123_secret_xK9...",
  "expires_at": "2026-05-12T17:30:00",
  "...": "..."
}
```

> **`client_secret` se devuelve UNA SOLA VEZ.** No aparece en `GET /v1/payments/{id}` ni en listados. Guárdalo en sesión, cookie firmada o pásalo al frontend inmediatamente.

### Ejemplo Node.js (backend)

```js
const resp = await fetch(`${process.env.RUTIVA_BASE_URL}/v1/payments`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${process.env.RUTIVA_SECRET_KEY}`,
    "Content-Type": "application/json",
    "Idempotency-Key": crypto.randomUUID(),
  },
  body: JSON.stringify({
    amount: 50000,
    currency: "VES",
    customer_phone: "04141234567",
    customer_id_document: "V12345678",
    customer_bank_code: "0114",
  }),
});
const intent = await resp.json();
// Enviar SOLO { id: intent.id, client_secret: intent.client_secret } al frontend.
```

### Ejemplo Python (backend)

```python
import httpx, os, uuid

resp = httpx.post(
    f"{os.environ['RUTIVA_BASE_URL']}/v1/payments",
    headers={
        "Authorization": f"Bearer {os.environ['RUTIVA_SECRET_KEY']}",
        "Idempotency-Key": str(uuid.uuid4()),
    },
    json={
        "amount": 50000,
        "currency": "VES",
        "customer_phone": "04141234567",
        "customer_id_document": "V12345678",
        "customer_bank_code": "0114",
    },
)
intent = resp.json()
```

### Idempotencia

El header `Idempotency-Key` (opcional pero recomendado) evita duplicar intents si tu request se reintenta por error de red.

- Misma key + mismo body → devuelve el intent existente con `HTTP 200` (sin nuevo `client_secret`).
- Misma key + body distinto → `HTTP 422 {"detail": "idempotency_key_mismatch"}`.
- Formato: max 100 chars, regex `^[A-Za-z0-9_\-:.]+$`. Recomendado: un UUID v4 por intento de pago lógico.

---

## 5. Confirmar el pago (frontend, `client_secret`)

`POST /v1/payments/{intent_id}/confirm`

El frontend recolecta el OTP que el cliente recibió por SMS de su banco, y confirma:

**Body:**
```json
{
  "client_secret": "pi_abc123_secret_xK9...",
  "otp": "123456"
}
```

**Sin `Authorization` header**. El `client_secret` es la autenticación. CORS abierto para este endpoint desde cualquier origen.

**Respuesta `200 OK`:**

```json
{
  "id": "8d3a...uuid",
  "status": "succeeded",
  "bank_reference": "MOCK-A1B2C3D4E5F6",
  "succeeded_at": "2026-05-12T17:18:42",
  "...": "..."
}
```

O bien:

```json
{
  "status": "failed",
  "failure_code": "bank_declined",
  "failure_message": "fondos_insuficientes"
}
```

### Ejemplo React

```jsx
async function confirmPayment(intentId, clientSecret, otp) {
  const resp = await fetch(
    `https://rutiva-api.onrender.com/v1/payments/${intentId}/confirm`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_secret: clientSecret, otp }),
    }
  );
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail);
  }
  return resp.json();
}
```

### Errores comunes en confirm

| HTTP | `detail` | Causa |
|---|---|---|
| 400 | `payment_expired` | Pasaron >15 min desde creación. Auto-cancelado. Crear uno nuevo. |
| 401 | `authentication_required` | Ni `sk_` ni `client_secret` en el request. |
| 403 | `invalid_client_secret` | El `client_secret` no corresponde a este `intent_id`, o es inválido. |
| 404 | `payment_intent_not_found` | El `intent_id` no existe. |
| 409 | `invalid_state:succeeded` | El intent ya fue confirmado/cancelado. No se puede reconfirmar. |

---

## 6. Confirmar desde el backend (alternativa sin widget)

Si prefieres no exponer ningún token al navegador, puedes recolectar el OTP en tu backend y confirmar con `sk_`:

```bash
curl -X POST https://rutiva-api.onrender.com/v1/payments/$INTENT_ID/confirm \
  -H "Authorization: Bearer sk_live_xxxx" \
  -H "Content-Type: application/json" \
  -d '{"otp":"123456"}'
```

En este modo, no envíes `client_secret`. Si envías ambos, prevalece `sk_`.

---

## 7. Cancelar un payment_intent (backend, `sk_`)

`POST /v1/payments/{intent_id}/cancel`

Solo aplica si el estado es `created`. Una vez `succeeded` o `failed`, no se puede cancelar.

```bash
curl -X POST https://rutiva-api.onrender.com/v1/payments/$INTENT_ID/cancel \
  -H "Authorization: Bearer sk_live_xxxx"
```

Dispara webhook `payment_intent.canceled`.

---

## 8. Consultar estado

`GET /v1/payments/{intent_id}` — requiere `sk_`.

`GET /v1/payments?limit=20&cursor=<b64>` — listado paginado por cursor. El cursor se obtiene del campo `next_cursor` de la respuesta anterior. `has_more=true` indica que quedan más resultados.

---

## 9. Webhooks (notificaciones server-to-server)

Rutiva notifica a tu backend cuando cambia el estado de un intent. Eventos emitidos:

- `payment_intent.created`
- `payment_intent.succeeded`
- `payment_intent.failed`
- `payment_intent.canceled`

### Registrar un endpoint

`POST /v1/webhook_endpoints` (requiere `sk_`):

```json
{
  "url": "https://tu-dominio.com/webhooks/rutiva",
  "enabled_events": ["payment_intent.succeeded", "payment_intent.failed"]
}
```

Filtros soportados:
- `["*"]` — todos los eventos.
- `["payment_intent.succeeded"]` — exacto.
- `["payment_intent.*"]` — wildcard por prefijo.

Respuesta (UNA SOLA VEZ):

```json
{
  "external_id": "whe_xxx",
  "url": "https://tu-dominio.com/webhooks/rutiva",
  "signing_secret": "whsec_xxxxxxxxxxxxxxx"
}
```

**Guarda `signing_secret` ahora**. No se puede recuperar después.

### Headers del webhook entrante

```
Content-Type: application/json
X-Rutiva-Signature: t=1715539200,v1=<sha256_hex>
X-Rutiva-Event-Type: payment_intent.succeeded
```

### Verificación de firma (estilo Stripe)

```python
import hmac, hashlib

def verify(body: bytes, header: str, secret: str, tolerance_seconds: int = 300) -> bool:
    parts = dict(p.split("=", 1) for p in header.split(","))
    t = int(parts["t"])
    v1 = parts["v1"]
    expected = hmac.new(
        secret.encode(),
        f"{t}.{body.decode()}".encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, v1):
        return False
    if abs(time.time() - t) > tolerance_seconds:
        return False  # rechaza replays viejos
    return True
```

Tu handler debe:
1. Leer el body **raw** (sin parsear JSON primero — la firma es sobre los bytes exactos).
2. Verificar firma + timestamp.
3. Responder `2xx` rápido (<10s). Si tardas más, Rutiva considera fallido el delivery.
4. Procesar el evento de forma idempotente (mismo evento puede llegar más de una vez).

### Ejemplo handler Express

```js
import crypto from "crypto";
import express from "express";

const app = express();

app.post(
  "/webhooks/rutiva",
  express.raw({ type: "application/json" }),
  (req, res) => {
    const header = req.header("X-Rutiva-Signature");
    const [tPart, v1Part] = header.split(",");
    const t = tPart.split("=")[1];
    const v1 = v1Part.split("=")[1];
    const body = req.body.toString();
    const expected = crypto
      .createHmac("sha256", process.env.RUTIVA_WEBHOOK_SECRET)
      .update(`${t}.${body}`)
      .digest("hex");
    if (!crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(v1))) {
      return res.status(400).send("invalid_signature");
    }
    const event = JSON.parse(body);
    // procesar event.type / event.data ...
    res.status(200).send("ok");
  }
);
```

---

## 10. Códigos de error

Todas las respuestas de error siguen el formato:

```json
{ "detail": "código_o_mensaje" }
```

| HTTP | Significado |
|---|---|
| 400 | Estado inválido o `payment_expired`. |
| 401 | Falta autenticación o API key inválida. |
| 403 | `no_default_account`, `invalid_client_secret`. |
| 404 | Recurso no existe o no pertenece al merchant. |
| 409 | Transición de estado no permitida (`invalid_state:<estado>`). |
| 422 | Validación de datos: formato venezolano inválido, `idempotency_key_mismatch`, etc. |
| 500 | Error interno. Reintentar con backoff exponencial. |

---

## 11. Buenas prácticas

1. **Nunca exponer `sk_` al navegador.** Usa el flujo `client_secret` o un proxy server-side.
2. **Idempotency-Key en cada create.** UUID v4 por intento lógico.
3. **Verificar firma de webhooks** siempre. Sin verificación, cualquiera puede forjar eventos.
4. **TLS obligatorio** en tu URL de webhook (`https://`).
5. **Manejo de expiración**: si tu UI demora más de 15 min entre create y confirm, crea un intent nuevo.
6. **Reintentos**: ante 5xx, reintenta con backoff. Ante 4xx, no reintentes — el error es del request.
7. **Logs**: registra `external_id` de cada intent. Sirve para soporte y reconciliación.
8. **Datos venezolanos**: valida en tu UI antes de mandar (regex local). Rutiva re-valida en el borde, pero te ahorra un round-trip.

---

## 12. Recursos

- Swagger UI interactivo: `https://rutiva-api.onrender.com/docs`
- Documentación pública (próximamente): `https://docs.rutiva.dev`
- Spec API detallada (en repo): `04-api-spec.md`
- Flujo C2P paso a paso: `05-flujo-c2p.md`
- Modelo de seguridad: `06-seguridad.md`
- Soporte: `dev@rutiva.dev`
