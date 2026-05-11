# 04 — API Specification

> **Versión**: v1
> **Base URL (sandbox)**: `https://api.pasarela.dev/v1`
> **Formato**: REST + JSON
> **Autenticación**: API Key (Bearer token)
> **Inspirada en**: Stripe API design principles

---

## Principios de diseño

1. **REST limpio**: recursos como sustantivos, acciones como verbos HTTP.
2. **Versionado en URL**: `/v1/` permite breaking changes en `/v2/` sin romper integraciones.
3. **IDs prefijados**: `pi_xxx`, `mch_xxx`, `evt_xxx` (autoexplicativos).
4. **Idempotencia obligatoria** en endpoints de escritura.
5. **Errores claros**: códigos semánticos + mensajes descriptivos en español.
6. **Paginación cursor-based** para listados largos.
7. **Webhooks firmados** con HMAC-SHA256.

---

## Autenticación

Toda llamada (excepto webhooks entrantes desde Bancaribe y endpoints públicos del dashboard) requiere el header:

```http
Authorization: Bearer sk_test_<clave_secreta>
```

Hay dos tipos de API key:
- **`pk_test_...`** / **`pk_live_...`**: publishable. Solo se usa en el frontend del comerciante (Checkout Widget). Solo permite crear `payment_intents` con monto/datos pre-aprobados.
- **`sk_test_...`** / **`sk_live_...`**: secret. Uso exclusivo en backend del comerciante. Acceso completo a la API.

**Nunca expongas un secret key en HTML, JavaScript del cliente, o repositorios públicos.**

---

## Idempotencia

Endpoints de escritura aceptan header `Idempotency-Key`:

```http
Idempotency-Key: cliente-orden-12345
```

Si el mismo `Idempotency-Key` llega dos veces (combinado con el mismo `sk`), se devuelve la respuesta original sin reprocesar. TTL: 24 horas.

**Obligatorio** en `POST /v1/payments`.

---

## Endpoints

### Payment Intents

#### `POST /v1/payments`

Crea un nuevo intent de cobro C2P.

**Request:**
```json
{
  "amount": 5000,
  "currency": "VES",
  "customer": {
    "phone": "04141234567",
    "id_document": "V12345678",
    "bank_code": "0114"
  },
  "metadata": {
    "order_id": "ORD-12345",
    "product_sku": "ZAPATO-001"
  }
}
```

**Notas**:
- `amount` está en céntimos (5000 = 50.00 VES). Esto evita errores de redondeo.
- `bank_code` es el código ABA del banco del cliente (no del comerciante).
- `metadata` es opcional, sirve para vincular con sistemas del comerciante.

**Response 201:**
```json
{
  "id": "pi_x9y8z7w6v5u4t3s2r1q0",
  "object": "payment_intent",
  "status": "created",
  "amount": 5000,
  "currency": "VES",
  "customer": {
    "phone": "0414****567",
    "id_document": "V*****678",
    "bank_code": "0114"
  },
  "client_secret": "pi_x9y8z7w6v5u4t3s2r1q0_secret_a1b2c3",
  "metadata": {
    "order_id": "ORD-12345",
    "product_sku": "ZAPATO-001"
  },
  "created_at": "2026-05-09T18:30:00Z",
  "expires_at": "2026-05-09T18:45:00Z"
}
```

**Notas**:
- `client_secret` se entrega al frontend para que el Widget pueda confirmar el pago sin exponer el `sk`.
- Datos sensibles (`phone`, `id_document`) se devuelven enmascarados.
- El intent expira automáticamente a los 15 minutos si no se confirma.

---

#### `POST /v1/payments/{id}/confirm`

Confirma el pago con la clave OTP del cliente. Este endpoint se llama desde el frontend (Widget) usando el `client_secret`.

**Request:**
```json
{
  "client_secret": "pi_x9y8z7w6v5u4t3s2r1q0_secret_a1b2c3",
  "otp": "123456"
}
```

**Response 200 (éxito):**
```json
{
  "id": "pi_x9y8z7w6v5u4t3s2r1q0",
  "object": "payment_intent",
  "status": "succeeded",
  "amount": 5000,
  "currency": "VES",
  "bank_reference": "BCRB-2026-0509-7890123",
  "succeeded_at": "2026-05-09T18:32:15Z"
}
```

**Response 402 (rechazado por banco):**
```json
{
  "error": {
    "type": "card_error",
    "code": "insufficient_funds",
    "message": "Fondos insuficientes en la cuenta del cliente.",
    "payment_intent": "pi_x9y8z7w6v5u4t3s2r1q0"
  }
}
```

**Response 400 (OTP inválido):**
```json
{
  "error": {
    "type": "invalid_request_error",
    "code": "invalid_otp",
    "message": "La clave OTP es incorrecta o ha expirado."
  }
}
```

---

#### `GET /v1/payments/{id}`

Consulta un payment intent específico.

**Response 200:**
```json
{
  "id": "pi_x9y8z7w6v5u4t3s2r1q0",
  "object": "payment_intent",
  "status": "succeeded",
  "amount": 5000,
  "currency": "VES",
  "customer": {
    "phone": "0414****567",
    "id_document": "V*****678",
    "bank_code": "0114"
  },
  "bank_reference": "BCRB-2026-0509-7890123",
  "metadata": { "order_id": "ORD-12345" },
  "created_at": "2026-05-09T18:30:00Z",
  "succeeded_at": "2026-05-09T18:32:15Z"
}
```

---

#### `GET /v1/payments`

Lista payment intents del comerciante.

**Query params:**
- `limit` (1-100, default 25)
- `starting_after` (cursor: el último ID de la página anterior)
- `status` (filtro: `created`, `pending`, `processing`, `succeeded`, `failed`, `canceled`)
- `created[gte]` y `created[lte]` (timestamps ISO 8601)

**Response 200:**
```json
{
  "object": "list",
  "has_more": true,
  "data": [
    { "id": "pi_xxx", "status": "succeeded", "amount": 5000, ... },
    { "id": "pi_yyy", "status": "failed", "amount": 12000, ... }
  ]
}
```

---

#### `POST /v1/payments/{id}/cancel`

Cancela un payment intent que aún no se ha procesado (estados `created` o `pending`).

**Response 200:**
```json
{
  "id": "pi_x9y8z7w6v5u4t3s2r1q0",
  "object": "payment_intent",
  "status": "canceled",
  "canceled_at": "2026-05-09T18:35:00Z"
}
```

---

### Webhooks

#### `POST /v1/webhook_endpoints`

Registra una URL para recibir notificaciones de eventos.

**Request:**
```json
{
  "url": "https://mi-tienda.com/webhooks/pasarela",
  "enabled_events": ["payment.succeeded", "payment.failed"]
}
```

`enabled_events` acepta valores específicos o `["*"]` para todos los eventos.

**Response 201:**
```json
{
  "id": "we_q7w8e9r0t1y2",
  "object": "webhook_endpoint",
  "url": "https://mi-tienda.com/webhooks/pasarela",
  "enabled_events": ["payment.succeeded", "payment.failed"],
  "signing_secret": "whsec_xxxxxxxxxxxxxxxxxxxxxxxx",
  "status": "active",
  "created_at": "2026-05-09T18:00:00Z"
}
```

**El `signing_secret` se devuelve UNA SOLA VEZ.** Guárdalo seguro — se usa para validar las firmas HMAC de los webhooks entrantes.

---

#### `GET /v1/webhook_endpoints`

Lista los endpoints configurados.

---

#### `DELETE /v1/webhook_endpoints/{id}`

Elimina un endpoint.

---

### API Keys

#### `POST /v1/api_keys`

Genera un nuevo par de API keys (publishable + secret).

**Request:**
```json
{
  "label": "Producción WooCommerce",
  "environment": "live"
}
```

**Response 201:**
```json
{
  "publishable_key": "pk_live_51HxYzABC...",
  "secret_key": "sk_live_51HxYzDEF...",
  "label": "Producción WooCommerce",
  "environment": "live",
  "created_at": "2026-05-09T18:00:00Z"
}
```

**El `secret_key` se devuelve UNA SOLA VEZ.** Si lo pierdes, debes generar uno nuevo y revocar el anterior.

---

#### `POST /v1/api_keys/{id}/revoke`

Revoca una API key. Llamadas con esa key fallarán con 401.

---

### Banks (recurso público)

#### `GET /v1/banks`

Lista los bancos cuyas claves OTP pueden ser validadas (corresponde a `listarBancosApi` de Bancaribe).

**Response 200:**
```json
{
  "object": "list",
  "data": [
    { "code": "0102", "name": "Banco de Venezuela" },
    { "code": "0105", "name": "Banco Mercantil" },
    { "code": "0114", "name": "Bancaribe" },
    { "code": "0134", "name": "Banesco" },
    { "code": "0163", "name": "Banco del Tesoro" },
    { "code": "0191", "name": "BNC" }
  ]
}
```

---

## Webhooks salientes

Cuando ocurre un evento, Pasarela hace un `POST` al `url` del `webhook_endpoint`.

**Headers:**
```http
Content-Type: application/json
Pasarela-Signature: t=1731234567,v1=abc123def456...
User-Agent: Pasarela/1.0
```

**Payload:**
```json
{
  "id": "evt_3f4g5h6j7k8l",
  "object": "event",
  "type": "payment.succeeded",
  "created_at": "2026-05-09T18:32:15Z",
  "data": {
    "object": {
      "id": "pi_x9y8z7w6v5u4t3s2r1q0",
      "amount": 5000,
      "currency": "VES",
      "status": "succeeded",
      ...
    }
  }
}
```

### Verificación de firma

El header `Pasarela-Signature` contiene `t=<timestamp>,v1=<hmac>`. Para validar:

```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    parts = dict(p.split("=") for p in signature_header.split(","))
    timestamp = parts["t"]
    expected = parts["v1"]
    
    signed_payload = f"{timestamp}.{payload.decode()}".encode()
    computed = hmac.new(
        secret.encode(),
        signed_payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed, expected)
```

### Reintentos

Si tu endpoint no devuelve `2xx`, Pasarela reintenta con backoff exponencial:

| Intento | Tiempo desde el primero |
|---|---|
| 1 | 0s (inmediato) |
| 2 | 1 minuto |
| 3 | 5 minutos |
| 4 | 15 minutos |
| 5 | 1 hora |
| 6 | 6 horas |
| 7 | 24 horas |

Después del séptimo intento, el webhook se marca como `failed` y debe re-enviarse manualmente desde el dashboard.

### Eventos disponibles

| Evento | Cuándo ocurre |
|---|---|
| `payment.created` | Se crea un nuevo payment intent |
| `payment.pending` | Cliente accedió al checkout |
| `payment.processing` | Se envió la solicitud a Bancaribe |
| `payment.succeeded` | Pago confirmado por el banco |
| `payment.failed` | Pago rechazado |
| `payment.canceled` | Pago cancelado (timeout o manual) |
| `webhook_endpoint.created` | Se registró un nuevo endpoint |

---

## Errores

Todos los errores siguen este formato:

```json
{
  "error": {
    "type": "<categoría>",
    "code": "<código_específico>",
    "message": "Mensaje legible en español",
    "param": "<campo_afectado_opcional>",
    "request_id": "req_xxx"
  }
}
```

### Categorías de error

| `type` | Descripción | HTTP Status |
|---|---|---|
| `invalid_request_error` | Petición mal formada o parámetros inválidos | 400 |
| `authentication_error` | API key inválida o ausente | 401 |
| `permission_error` | API key válida pero sin permisos | 403 |
| `not_found_error` | Recurso no existe | 404 |
| `rate_limit_error` | Demasiadas peticiones | 429 |
| `card_error` | Error procesando el pago (rechazo del banco) | 402 |
| `api_error` | Error interno de Pasarela | 500 |
| `bank_error` | Error de Bancaribe (timeout, indisponibilidad) | 502 |

### Códigos específicos comunes

| `code` | Descripción |
|---|---|
| `invalid_phone` | Teléfono no cumple formato `04XXXXXXXXX` |
| `invalid_id_document` | Cédula no cumple formato `[VEJGP]\d+` |
| `invalid_bank_code` | Banco no soportado |
| `invalid_amount` | Monto fuera de rango |
| `invalid_otp` | Clave OTP incorrecta o expirada |
| `insufficient_funds` | Fondos insuficientes |
| `account_blocked` | Cuenta del cliente bloqueada |
| `payment_already_processed` | Intent ya en estado final |
| `payment_expired` | Intent expiró antes de confirmarse |
| `bank_timeout` | Bancaribe no respondió a tiempo |

---

## Rate limits

| Tier | Requests por minuto | Requests por segundo |
|---|---|---|
| Test environment | 60 | 5 |
| Live (default) | 300 | 25 |
| Live (high-volume) | 1000 | 50 |

Headers de respuesta:
```http
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 287
X-RateLimit-Reset: 1731234600
```

---

## OpenAPI / Swagger

La especificación completa en formato OpenAPI 3.1 está disponible en:
```
https://api.pasarela.dev/openapi.json
```

Swagger UI en:
```
https://api.pasarela.dev/docs
```

---

## SDKs (Fase 1 vs roadmap)

| Lenguaje | Estado |
|---|---|
| JavaScript / TypeScript (browser y Node) | ✅ MVP |
| Python | 🟡 Fase 1 (después de MVP) |
| PHP | 🟡 Fase 1 |
| Plugin WooCommerce | 🟡 Fase 1 |
| Plugin Shopify | 🟡 Fase 2 |
| Plugin Magento / PrestaShop | 🟡 Fase 2 |
| Go / Ruby / Java | 🔵 Fase 2+ según demanda |
