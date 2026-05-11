Actúa como un Senior Backend Engineer experto en Python y FastAPI. Estamos construyendo "Pasarela", una pasarela de pagos C2P en Venezuela. La base de datos y los modelos SQLAlchemy ya están configurados y refactorizados en `app/models/`.

Tu objetivo ahora es implementar el **Bank Adapter (Strategy Pattern)** y los **Endpoints Core de Pagos**, correspondientes al bloque de desarrollo actual.

Por favor, sigue estas instrucciones paso a paso para crear y modificar los archivos necesarios. Escribe código de producción, fuertemente tipado, asíncrono y utilizando inyección de dependencias de FastAPI.

### PASO 1: Implementar el Bank Adapter
Crea el módulo `app/banking/` con la siguiente estructura:

1. **`app/banking/schemas.py`**:
   - Define los esquemas Pydantic para la comunicación con el banco:
     - `C2PRequest`: `merchant_account` (str), `customer_phone` (str), `customer_id` (str), `customer_bank` (str), `otp` (str), `amount_cents` (int), `currency` (str), `reference` (str).
     - `C2PResponse`: `reference` (str), `status` (str).
     - `OperationStatus`: `status` (str).

2. **`app/banking/base.py`**:
   - Crea una clase abstracta `BankAdapter(ABC)`.
   - Define los métodos asíncronos abstractos: `initiate_c2p(self, req: C2PRequest) -> C2PResponse`, `query_operation(self, ref: str) -> OperationStatus`, `list_supported_banks(self) -> list[dict]`.
   - Define una property abstracta: `supports_aggregator_mode(self) -> bool`.

3. **`app/banking/mock.py`**:
   - Implementa `MockBankAdapter` heredando de `BankAdapter`.
   - En `initiate_c2p`, simula un `asyncio.sleep` de 1 a 3 segundos, y devuelve un éxito (`aprobado` y un reference ID aleatorio) el 80% de las veces. El 20% restante, lanza un ValueError simulando fondos insuficientes.
   - En `list_supported_banks` devuelve una lista básica de bancos (ej. Bancaribe 0114, BNC 0191, Mercantil 0105).

### PASO 2: Schemas de la API
Crea `app/schemas/payment.py` para los requests/responses de la API pública:
- `PaymentCreateRequest`: `amount` (int > 0), `currency` (str: VES/USD), `customer_phone`, `customer_id_document`, `customer_bank_code`.
- `PaymentConfirmRequest`: `client_secret` (str), `otp` (str).
- `PaymentResponse`: Esquema de respuesta que devuelva los datos del PaymentIntent (id, status, amount, currency, etc.). Pista: usa `model_config = ConfigDict(from_attributes=True)`.

### PASO 3: Endpoints Core
Crea `app/api/v1/payments.py` (usa `APIRouter` de FastAPI):
- Define la dependencia de base de datos (`Depends(get_db)` de `app.database`).
- (Por ahora, omite el middleware real de API Keys, usa un stub o dependencia dummy para no bloquear la creación de los endpoints).
- Implementa `POST /v1/payments`: Recibe `PaymentCreateRequest`, instancia un `MockBankAdapter` (luego lo inyectaremos correctamente), inserta un `PaymentIntent` en estado `created` en la DB y hace el commit. Retorna el objeto.
- Implementa `POST /v1/payments/{id}/confirm`: Recibe `PaymentConfirmRequest`. Busca el intent en DB. Llama al `MockBankAdapter.initiate_c2p`. Actualiza el estado del intent a `succeeded` o `failed` según la respuesta. Retorna el objeto.
- Implementa `GET /v1/payments/{id}`: Retorna un intent por ID.

### PASO 4: Punto de entrada
Crea o actualiza `app/main.py`:
- Inicializa la aplicación FastAPI con el título "Pasarela API".
- Incluye el router de payments (`app.include_router(...)`).
- Agrega un endpoint base `GET /health` que retorne `{"status": "ok"}`.

Dame un resumen de los archivos creados/modificados y confirma si el servidor levanta correctamente al ejecutar `uvicorn app.main:app --reload`.