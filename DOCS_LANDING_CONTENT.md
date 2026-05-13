# Contenido para documentación pública (landing)

> **Audiencia**: developers externos que integran Rutiva en sus apps.
>
> **Qué incluye**: lo mínimo que un usuario público necesita para integrarse exitosamente.
>
> **Qué NO incluye** (intencional): arquitectura interna, Alembic/migrations, Render/Supabase, seed scripts, endpoints admin, modelo de datos, Sentry, deploy, decisiones de stack.
>
> Mapea 1:1 a las rutas definidas en `PROMPT_DOCS_PAGE.md`. Cada sección de abajo = una página `/docs/<slug>`.

---

## Datos comunes

- **Base URL producción**: `https://rutiva-api.onrender.com`
- **Versión actual**: `v0.1.0` (MVP)
- **Estado**: ambiente `test` con MockBankAdapter. Producción real (Bancaribe Open Banking) en integración.
- **Banco soportado actual**: Bancaribe (`0114`).
- **Swagger interactivo**: `https://rutiva-api.onrender.com/docs`

---

## Página: `/docs/introduccion`

**Slug**: `introduccion` · **Título**: "Introducción" · **Orden**: 1

### Qué es Rutiva

Rutiva es una API de pagos **C2P (Customer-to-Payment)** para el ecosistema venezolano. Permite a comerciantes aceptar pagos desde cualquier banco venezolano usando el flujo OTP-bancario estándar, con una experiencia developer-first inspirada en las mejores prácticas globales.

### Conceptos clave

| Concepto | Descripción |
|---|---|
| `payment_intent` | Pago en curso. Ciclo: `created → succeeded \| failed \| canceled`. |
| `sk_xxx` | **Secret key**. Solo en tu backend. Crea intents, consulta, cancela. |
| `client_secret` | Token de un solo uso vinculado a un intent. El navegador lo usa para confirmar sin exponer `sk_`. |
| `whsec_xxx` | Signing secret del webhook. Verifica que las notificaciones vienen de Rutiva. |
| OTP | Código que el banco del cliente envía por SMS. El cliente lo escribe en tu UI para confirmar. |

### Flujo recomendado

```
1. Tu backend       ──crear intent (sk_)──▶   Rutiva API
                    ◀──   client_secret  ──

2. Tu backend pasa client_secret al navegador del cliente.

3. Navegador (Widget) ──confirmar (client_secret + OTP)──▶ Rutiva API
                       ◀──── payment_intent.succeeded ────
```

El backend mantiene la `sk_` segura. El navegador solo maneja un token de un solo uso atado a ese intent específico.

### Próximo paso

Continuá con [Autenticación](/docs/autenticacion).

---

## Página: `/docs/autenticacion`

**Slug**: `autenticacion` · **Título**: "Autenticación" · **Orden**: 2

### API keys

Rutiva emite dos tipos de credenciales por comerciante:

- **`sk_test_...`** — ambiente de pruebas. MockBankAdapter responde 80% éxito / 20% fallo aleatorio.
- **`sk_live_...`** — ambiente real. Conectado a Bancaribe Open Banking.

### Cómo obtener tus llaves

Durante el MVP las credenciales se entregan manualmente. Solicitalas desde la sección de contacto del landing.

> **Importante**: la `sk_` solo se muestra **una vez** al momento de crearla. No se puede recuperar. Guardala inmediatamente en tu password manager y en las variables de entorno de tu servidor.

### Uso

```http
Authorization: Bearer sk_test_xxxxxxxxxxxxxxxxxxxxxxxxx
```

Aceptado también como header alternativo:

```http
X-API-Key: sk_test_xxxxxxxxxxxxxxxxxxxxxxxxx
```

### Reglas críticas de seguridad

1. **Nunca** incluyas `sk_` en código frontend, bundles JS, repos públicos, ni logs.
2. Guardala en variables de entorno del servidor: `RUTIVA_SECRET_KEY=sk_xxx`.
3. Si exponés una `sk_` por error, contactá soporte para rotarla.
4. Rotá tus keys periódicamente.

### Endpoints públicos sin autenticación

- `GET /v1/banks` — lista de bancos soportados.
- `POST /v1/payments/{id}/confirm` — confirmación vía `client_secret` desde browser (la autenticación es el propio `client_secret`).
- `GET /health`, `GET /ping` — utilidades.

Todo el resto requiere `sk_`.

---

## Página: `/docs/bancos`

**Slug**: `bancos` · **Título**: "Lista de bancos" · **Orden**: 3

### `GET /v1/banks`

Lista pública de bancos venezolanos soportados. **Sin autenticación**, CORS abierto. Útil para poblar un dropdown en tu UI sin hardcodear códigos.

**Request:**

```http
GET https://rutiva-api.onrender.com/v1/banks
```

**Response `200`:**

```json
{
  "object": "list",
  "data": [
    { "code": "0114", "name": "Bancaribe" }
  ]
}
```

> **Estado MVP**: solo Bancaribe está habilitado. La lista crecerá conforme se integren más adquirentes (BNC, Mercantil, Banco de Venezuela, Provincial están en roadmap). **Tu UI debe leer dinámicamente** este endpoint, no hardcodear la lista.

### Ejemplo JS

```js
const res = await fetch("https://rutiva-api.onrender.com/v1/banks");
const { data: banks } = await res.json();
// banks = [{ code: "0114", name: "Bancaribe" }]
```

### Cache

La respuesta cambia raramente. Podés cachearla en tu cliente por 1 hora.

---

## Página: `/docs/crear-pago`

**Slug**: `crear-pago` · **Título**: "Crear pago" · **Orden**: 4

### `POST /v1/payments`

Crea un `payment_intent` en estado `created`. Requiere `sk_`.

**Headers:**

```http
Authorization: Bearer sk_live_xxxxxxxx
Content-Type: application/json
Idempotency-Key: <opcional pero recomendado>
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

### Campos

| Campo | Tipo | Validación |
|---|---|---|
| `amount` | int | Céntimos. `≥ 1`, `≤ 100_000_000_000` (mil millones). Ejemplo: `50000` = Bs. 500,00. |
| `currency` | string | `"VES"` o `"USD"`. |
| `customer_phone` | string | Formato `04XXXXXXXXX` (11 dígitos). |
| `customer_id_document` | string | `V/E/J/G/P` + 6-9 dígitos. Se normaliza a mayúsculas automáticamente. |
| `customer_bank_code` | string | Código de 4 dígitos. Debe estar listado en `/v1/banks`. |

### Response `201 Created`

```json
{
  "id": "8d3a4b5c-2e74-41f6-a091-f7036f8d6a8c",
  "external_id": "pi_L9limdfjZ6SHJjpkXueO1w",
  "status": "created",
  "amount_cents": 50000,
  "currency": "VES",
  "customer_phone": "04141234567",
  "customer_id_document": "V12345678",
  "customer_bank_code": "0114",
  "expires_at": "2026-05-13T15:30:00",
  "client_secret": "pi_L9limdfjZ6SHJjpkXueO1w_secret_tjxQABDZZWMokatGobBsZocUItksOJIZ",
  "created_at": "2026-05-13T15:15:00",
  "updated_at": "2026-05-13T15:15:00"
}
```

> **`client_secret`** se devuelve **una sola vez**. No aparece en `GET /v1/payments/{id}` ni en listados. Guardalo en sesión o pásalo al frontend de inmediato.

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
// Enviar solo { id: intent.id, client_secret: intent.client_secret } al frontend.
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

El header `Idempotency-Key` evita duplicar intents si un request se reintenta por error de red.

- Misma key + body idéntico → devuelve el intent existente con `HTTP 200`. **El `client_secret` no se incluye** en el replay (solo en la creación original).
- Misma key + body distinto → `HTTP 422 {"detail":"idempotency_key_mismatch"}`.
- Formato: max 100 chars, regex `^[A-Za-z0-9_\-:.]+$`. Recomendado: UUID v4 por intento de pago lógico.

### Expiración

Cada intent expira a los **15 minutos** de creación (`expires_at` en la respuesta). Pasado ese tiempo, intentar confirmar devuelve `400 payment_expired` y el intent queda `canceled` automáticamente.

---

## Página: `/docs/confirmar-pago`

**Slug**: `confirmar-pago` · **Título**: "Confirmar pago" · **Orden**: 5

### `POST /v1/payments/{intent_id}/confirm`

Confirma el pago con el OTP que el banco envió al cliente.

> `{intent_id}` acepta el UUID interno o el `external_id` (`pi_xxx`). Estilo Stripe.

### Modo Widget (frontend, sin `sk_`)

Recomendado para flujos donde el cliente final escribe el OTP en una UI servida en tu sitio.

**Headers:**

```http
Content-Type: application/json
```

**Sin** `Authorization`. El `client_secret` es la autenticación.

**Body:**

```json
{
  "client_secret": "pi_L9limdfjZ6SHJjpkXueO1w_secret_tjxQABDZZWMokatGobBsZocUItksOJIZ",
  "otp": "123456"
}
```

CORS abierto para este endpoint desde cualquier origen.

### Modo Backend (con `sk_`)

Si preferís recolectar el OTP en tu backend (más seguro pero menos UX):

```http
Authorization: Bearer sk_live_xxxx
Content-Type: application/json
```

```json
{ "otp": "123456" }
```

Si enviás `sk_` **y** `client_secret`, prevalece `sk_`.

### Response `200 OK`

Éxito:

```json
{
  "id": "8d3a4b5c-2e74-41f6-a091-f7036f8d6a8c",
  "external_id": "pi_L9limdfjZ6SHJjpkXueO1w",
  "status": "succeeded",
  "bank_reference": "MOCK-A1B2C3D4E5F6",
  "succeeded_at": "2026-05-13T15:18:42",
  "amount_cents": 50000,
  "currency": "VES"
}
```

Rechazo del banco:

```json
{
  "status": "failed",
  "failure_code": "bank_declined",
  "failure_message": "fondos_insuficientes",
  "failed_at": "2026-05-13T15:18:42"
}
```

### Errores

| HTTP | `detail` | Causa | Solución |
|---|---|---|---|
| 400 | `payment_expired` | Pasaron >15 min. Auto-cancelado. | Crear nuevo intent. |
| 401 | `authentication_required` | Ni `sk_` ni `client_secret`. | Adjuntar uno. |
| 403 | `invalid_client_secret` | `client_secret` no corresponde al intent del path. | Verificar pares matching. |
| 404 | `payment_intent_not_found` | `intent_id` no existe. | Verificar valor. |
| 409 | `invalid_state:<estado>` | Ya `succeeded`/`failed`/`canceled`. | No reconfirmar. |

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

### Modo ambiente test (MockBankAdapter)

Mientras estés en `sk_test_`, el OTP **no se valida**. Pasá cualquier valor de 4-12 caracteres. El resultado es aleatorio: ~80% `succeeded`, ~20% `failed` con `failure_message=fondos_insuficientes`. Latencia simulada: 1-3 segundos.

---

## Página: `/docs/cancelar-pago`

**Slug**: `cancelar-pago` · **Título**: "Cancelar pago" · **Orden**: 6

### `POST /v1/payments/{intent_id}/cancel`

Cancela un intent en estado `created`. **Solo modo backend** (requiere `sk_`). No se puede cancelar desde el navegador.

**Headers:**

```http
Authorization: Bearer sk_live_xxxx
```

**Body:** vacío.

### Response `200`

```json
{
  "id": "8d3a4b5c-...",
  "external_id": "pi_L9limdfjZ6SHJjpkXueO1w",
  "status": "canceled",
  "canceled_at": "2026-05-13T15:16:00"
}
```

### Errores

| HTTP | `detail` | Causa |
|---|---|---|
| 400 | `invalid_state:<estado>` | Solo se cancela en `created`. Ya `succeeded`/`failed`/`canceled` → 400. |
| 401 | `invalid_api_key` | `sk_` falta o inválida. |
| 404 | `payment_intent_not_found` | No existe o no es tuyo. |

### Webhook

Cancelar dispara el evento `payment_intent.canceled` a tus endpoints suscritos.

---

## Página: `/docs/consultar-pago`

**Slug**: `consultar-pago` · **Título**: "Consultar pagos" · **Orden**: 7

### `GET /v1/payments/{intent_id}`

Detalle de un intent. Requiere `sk_`. `{intent_id}` acepta UUID o `external_id`.

```bash
curl https://rutiva-api.onrender.com/v1/payments/pi_xxx \
  -H "Authorization: Bearer sk_live_xxxx"
```

Response idéntica al objeto `payment_intent` pero **sin `client_secret`** (nunca aparece en GET).

### `GET /v1/payments?limit=20&cursor=<b64>`

Listado paginado de todos tus intents. Ordenado por `created_at DESC, id DESC`.

**Query params:**

| Param | Default | Notas |
|---|---|---|
| `limit` | `20` | Entre 1 y 100. |
| `cursor` | (vacío) | Opaque base64. Usá el `next_cursor` de la respuesta anterior. |

**Response:**

```json
{
  "items": [ { "id": "...", "external_id": "pi_...", "status": "succeeded", "..." } ],
  "next_cursor": "MjAyNi0...",
  "has_more": true
}
```

Cuando `has_more=false`, no hay más páginas y `next_cursor=null`.

---

## Página: `/docs/webhooks`

**Slug**: `webhooks` · **Título**: "Webhooks" · **Orden**: 8

### Qué son

Rutiva envía notificaciones HTTP a tu servidor cuando cambia el estado de un payment_intent. Esencial para flujos asíncronos: reconciliación, cumplimiento de pedidos, notificaciones al usuario.

### Eventos emitidos

- `payment_intent.created`
- `payment_intent.succeeded`
- `payment_intent.failed`
- `payment_intent.canceled`

### Registrar tu endpoint receptor

`POST /v1/webhook_endpoints` (requiere `sk_`):

```json
{
  "url": "https://tu-dominio.com/webhooks/rutiva",
  "enabled_events": ["payment_intent.succeeded", "payment_intent.failed"]
}
```

Filtros soportados en `enabled_events`:

- `["*"]` — todos los eventos.
- `["payment_intent.succeeded"]` — exacto.
- `["payment_intent.*"]` — wildcard por prefijo.

**Response `201`:**

```json
{
  "external_id": "whe_xxx",
  "url": "https://tu-dominio.com/webhooks/rutiva",
  "signing_secret": "whsec_xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

> **Guardá `signing_secret` ahora.** No se puede recuperar después.

### Headers entrantes

Cada notificación llega con:

```http
Content-Type: application/json
X-Rutiva-Signature: t=1715539200,v1=<sha256_hex>
X-Rutiva-Event-Type: payment_intent.succeeded
```

### Verificación de firma (estilo Stripe)

```
v1 = HMAC_SHA256(signing_secret, f"{t}.{body}")
```

Tu handler debe:

1. Leer el body **raw** (sin parsear JSON antes — la firma es sobre los bytes exactos).
2. Recalcular HMAC con tu `signing_secret` guardado.
3. Comparar con `v1` usando comparación **timing-safe** (`hmac.compare_digest` / `crypto.timingSafeEqual`).
4. Rechazar si `t` es muy viejo (>5 min) para mitigar replays.
5. Responder `2xx` rápido (<10s). Procesar el evento idempotentemente.

### Ejemplo Express

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
    if (Math.abs(Date.now() / 1000 - parseInt(t, 10)) > 300) {
      return res.status(400).send("timestamp_out_of_tolerance");
    }
    const event = JSON.parse(body);
    // procesar event.type, event.data ...
    res.status(200).send("ok");
  }
);
```

### Ejemplo Python (FastAPI)

```python
import hashlib, hmac, time
from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI()
SECRET = os.environ["RUTIVA_WEBHOOK_SECRET"]

@app.post("/webhooks/rutiva")
async def receive(
    request: Request,
    x_rutiva_signature: str = Header(...),
):
    body = await request.body()
    parts = dict(p.split("=", 1) for p in x_rutiva_signature.split(","))
    t = int(parts["t"])
    expected = hmac.new(
        SECRET.encode(), f"{t}.{body.decode()}".encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, parts["v1"]):
        raise HTTPException(400, "invalid_signature")
    if abs(time.time() - t) > 300:
        raise HTTPException(400, "timestamp_out_of_tolerance")
    event = json.loads(body)
    # procesar ...
    return {"received": True}
```

### Notas

- TLS obligatorio en la URL receptora (`https://`).
- Si tu endpoint falla (no responde 2xx), por ahora **no se reintenta** en MVP. Reintentos durables vienen en próxima versión.
- El mismo evento puede llegar más de una vez en el futuro (cuando se habiliten retries). Procesá idempotentemente.

---

## Página: `/docs/errores`

**Slug**: `errores` · **Título**: "Códigos de error" · **Orden**: 9

Todas las respuestas de error siguen el formato:

```json
{ "detail": "código_o_mensaje" }
```

### Códigos HTTP

| HTTP | Significado | Acción típica |
|---|---|---|
| `400` | Petición válida pero estado/timing inválido. Ej: `payment_expired`. | No reintentar. Crear nuevo recurso o cambiar request. |
| `401` | Falta autenticación o `sk_` inválida. | Verificar header `Authorization` o `client_secret`. |
| `403` | Autenticado pero sin permisos: `invalid_client_secret`, `no_default_account`. | No reintentar con la misma credencial. |
| `404` | Recurso no existe o no te pertenece. | Verificar `intent_id`. |
| `409` | Transición de estado inválida: `invalid_state:<estado>`. | Estado actual no permite la operación. |
| `422` | Validación de datos. Formato venezolano inválido, `idempotency_key_mismatch`, etc. | Corregir body y reintentar. |
| `500` | Error interno del servidor. | Reintentar con backoff exponencial (1s, 2s, 4s, 8s, …). |
| `503` | Servicio temporalmente no disponible. | Reintentar con backoff. |

### Errores específicos

| `detail` | Endpoint | Causa | Solución |
|---|---|---|---|
| `invalid_api_key` | cualquiera | `sk_` revocada o inexistente. | Solicitar nueva. |
| `idempotency_key_mismatch` | `POST /v1/payments` | Misma key, body distinto. | Usar key nueva para body distinto. |
| `invalid_idempotency_key` | `POST /v1/payments` | Formato inválido (>100 chars o caracteres no permitidos). | Usar UUID v4 o similar. |
| `payment_expired` | `POST .../confirm` | `>15 min` desde creación. | Crear nuevo intent. |
| `invalid_client_secret` | `POST .../confirm` | `client_secret` no matchea el intent. | Verificar pareo correcto. |
| `invalid_state:<estado>` | `POST .../confirm`, `.../cancel` | Estado actual no permite la operación. | No reintentar; estado terminal. |
| `payment_intent_not_found` | varios | `intent_id` no existe o no es del merchant autenticado. | Verificar valor. |

---

## Página: `/docs/buenas-practicas`

**Slug**: `buenas-practicas` · **Título**: "Buenas prácticas" · **Orden**: 10

Checklist para integraciones de producción:

### Seguridad

- [ ] **`sk_` solo en variables de entorno del servidor.** Nunca en repos, bundles JS, o logs.
- [ ] **Verificá firma de webhooks siempre.** Sin verificación, cualquiera puede simular eventos.
- [ ] **TLS obligatorio** en URLs de webhook receptoras.
- [ ] **Rotación de keys** periódica. Si exponés una key, contactá soporte.
- [ ] **No loguees `client_secret` ni OTPs.** Sensibles.

### Robustez

- [ ] **`Idempotency-Key` en cada create**, idealmente UUID v4 por intento lógico. Evita cobros dobles.
- [ ] **Reintentos con backoff exponencial** ante `5xx`. Nunca ante `4xx`.
- [ ] **Manejo de expiración**: si tu UI demora más de 15 min, crea un intent nuevo.
- [ ] **Procesamiento idempotente de webhooks**: el mismo evento puede llegar más de una vez (en futuras versiones).
- [ ] **Logueá `external_id`** (`pi_xxx`) de cada intent. Sirve para soporte y reconciliación.

### Validación

- [ ] **Validá datos venezolanos en tu UI** antes de mandar (regex local): teléfono `^04\d{9}$`, cédula `^[VEJGP]\d{6,9}$`, RIF `^[VEJGP]-\d{8}-\d$`. Rutiva re-valida en el borde, pero te ahorra round-trips.
- [ ] **`amount` en céntimos**, no decimales. Bs. 500,00 = `50000`.
- [ ] **Currency case-sensitive**: `"VES"` o `"USD"` mayúsculas.

### UX

- [ ] **Poblá el dropdown de bancos dinámicamente** desde `/v1/banks`. No hardcodees.
- [ ] **Mostrá `bank_reference`** al cliente tras `succeeded`. Es la referencia bancaria, útil para soporte.
- [ ] **Mostrá `failure_message`** legible tras `failed`. Mensajes vienen del banco.
- [ ] **Loading state** durante el confirm — el banco demora 1-3s en responder.

---

## Datos compartidos para todas las páginas

### Tipos de objeto

#### `PaymentIntent`

```ts
type PaymentIntent = {
  id: string;                    // UUID interno
  external_id: string;           // pi_xxx
  status: "created" | "succeeded" | "failed" | "canceled";
  amount_cents: number;
  currency: "VES" | "USD";
  customer_phone: string;
  customer_id_document: string;
  customer_bank_code: string;
  bank_reference: string | null;       // solo en succeeded
  failure_code: string | null;          // solo en failed
  failure_message: string | null;       // solo en failed
  expires_at: string;                   // ISO datetime, 15 min post-create
  created_at: string;
  updated_at: string;
  confirmed_at: string | null;
  succeeded_at: string | null;
  failed_at: string | null;
  canceled_at: string | null;
  // client_secret aparece SOLO en la response del create.
};
```

#### `Bank`

```ts
type Bank = {
  code: string;   // "0114"
  name: string;   // "Bancaribe"
};
```

#### `WebhookEvent`

```ts
type WebhookEvent = {
  type: "payment_intent.created"
      | "payment_intent.succeeded"
      | "payment_intent.failed"
      | "payment_intent.canceled";
  data: PaymentIntent;
};
```

### Variables de entorno típicas

```bash
# Backend del comerciante
RUTIVA_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxx
RUTIVA_BASE_URL=https://rutiva-api.onrender.com
RUTIVA_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx

# Frontend
VITE_RUTIVA_PUBLISHABLE_KEY=pk_xxx        # widget usa como identificador
VITE_RUTIVA_BASE_URL=https://rutiva-api.onrender.com
```

### Recursos

- Swagger interactivo: `https://rutiva-api.onrender.com/docs`
- Estado del servicio: `https://rutiva-api.onrender.com/health`
- Soporte: `dev@rutiva.dev` (ajustar)
