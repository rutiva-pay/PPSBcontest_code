# Plan Diario — 8 Días para Shark Bank

> **Cierre**: 17 de mayo de 2026
> **Envío recomendado**: 16 de mayo (margen de seguridad)
> **Equipo**: Roberto (Engineering Lead) + Co-founder (Business & Design Lead)

Este documento divide las 8 jornadas en tareas concretas. Cada día tiene un objetivo claro y entregables verificables. La regla de oro: **al final del día, debe existir algo demostrable, no solo "trabajado"**.

---

## Reglas de la semana

1. **12 horas productivas máximo por día.** 7 horas de sueño no negociables.
2. **Time-boxing estricto.** Si una tarea no termina en su bloque, sigue adelante.
3. **No agregar features.** Toda idea nueva va a `IDEAS.md` para Fase 1.
4. **Commit diario al repo.** Visibilidad pública es credibilidad.
5. **Standup matutino** (15 min) entre Roberto y co-founder: qué hiciste ayer, qué harás hoy, bloqueos.
6. **Demo al final del día.** Aunque sea solo entre ustedes dos, ver el progreso construye momentum. API keys
  - Webhooks

---

## Día 1 — Sábado 10 de mayo — Fundamentos ✅ (HOY)

**Objetivo**: tener toda la estructura, documentación y planeación lista para arrancar con código mañana.

### Roberto (12h)

- [x] Crear estructura del monorepo.
- [x] README principal del repo.
- [x] Documento de Visión Técnica (01).
- [x] Documento de Arquitectura con diagrama C4 (02).
- [x] Modelo de datos con ER diagram (03).
- [x] API Specification (04).
- [x] Flujo C2P end-to-end (05).
- [x] Modelo de Seguridad (06).
- [x] Roadmap (07).
- [x] Marco Regulatorio (08).
- [x] Análisis de Mercado (09).
- [x] Borrador del formulario de aplicación.
- [x] requirements.txt + .env.example + .gitignore.
- [x] Docker Compose para desarrollo local.
- [x] **Crear cuentas**: GitHub repo, Vercel, Railway, Supabase, Resend, Sentry, Cloudflare.
- [x] **Push inicial al repo público** con toda esta documentación.

### Co-founder (12h)

- [ ] **Revisión y feedback** sobre todos los documentos generados hoy (especialmente Visión Técnica y borrador de formulario).
- [ ] **Identidad visual placeholder**:
  - Paleta de colores: 2 primarios, 2 secundarios, neutros.
  - Tipografía (sugerencia: Inter para todo).
  - Logo simple (Canva o herramienta IA, 30 min máximo — no perfeccionar).
- [ ] **Wireframes en Figma** del dashboard:
  - Login
  - Overview (con cards de métricas)
  - Lista de transacciones
  - Detalle de transacción
  - API keys
  - Webhooks
- [ ] **Investigación complementaria**: posibles nombres del producto (10 candidatos + verificación de dominios disponibles).
- [ ] **Crear cuentas placeholder** en Instagram y LinkedIn (sin contenido aún, solo reservar el nombre).

### Entregables fin de día 1
- Repo GitHub público con toda la documentación commiteada.
- Cuentas SaaS necesarias creadas.
- Wireframes Figma básicos del dashboard.
- 10 candidatos de nombre con dominios verificados.

---

## Día 2 — Domingo 11 de mayo — Backend Core

**Objetivo**: tener el backend FastAPI funcionando localmente con los endpoints principales (con mock de Bancaribe).

### Roberto (12h)

#### Bloque mañana (4h): Setup y modelos

- [ ] Crear virtual environment Python 3.12 + instalar requirements.
- [ ] Configurar SQLAlchemy 2.0 + Alembic.
- [ ] Crear modelos: `Merchant`, `ApiKey`, `MerchantAccount`, `PaymentIntent`, `WebhookEndpoint`, `WebhookAttempt`, `Event`.
- [ ] Migración inicial con Alembic.
- [ ] Levantar Postgres con Docker Compose.
- [ ] Aplicar migración exitosamente.

#### Bloque mediodía (4h): Bank Adapter + endpoints core

- [ ] `BankAdapter` base abstracta en `app/banking/base.py`.
- [ ] `MockBankAdapter` que simula respuestas de Bancaribe (80% éxito aleatorio, latencia 1-3s).
- [ ] `BancaribeAdapter` stub (solo estructura, llamada real para Día 7).
- [ ] Endpoint `POST /v1/payments` (crear payment intent).
- [ ] Endpoint `POST /v1/payments/{id}/confirm` (confirmar con OTP).
- [ ] Endpoint `GET /v1/payments/{id}`.
- [ ] Endpoint `GET /v1/payments` (con paginación cursor-based).
- [ ] Middleware de autenticación con API Key.

#### Bloque tarde (4h): Webhooks y eventos

- [ ] `WebhookService` con dispatcher usando `BackgroundTasks`.
- [ ] Firma HMAC-SHA256 en webhooks.
- [ ] Outbox pattern: tabla `webhook_attempts` poblada en misma transacción.
- [ ] Endpoint `POST /v1/webhook_endpoints`.
- [ ] Endpoint `GET /v1/webhook_endpoints`.
- [ ] `EventService` que inserta en tabla `events` en cada cambio.
- [ ] Test manual end-to-end con cURL/Postman: crear → confirmar → ver webhook llegando.

### Co-founder (12h)

#### Pitch deck V1 (5h)

- [ ] 12 slides en Pitch.com o Google Slides:
  1. Portada (logo + tagline)
  2. El problema
  3. Por qué ahora
  4. La solución
  5. Demo (screenshot + QR)
  6. Cómo funciona
  7. Diferenciador
  8. Modelo de negocio
  9. Mercado y competencia
  10. Roadmap (3 fases)
  11. Por qué Bancaribe
  12. El equipo + pedido

#### Identidad visual final (4h)

- [ ] Logo definitivo placeholder (puede iterarse Día 5 cuando se decida nombre real).
- [ ] Paleta de colores aplicable a:
  - Dashboard
  - Landing page
  - Checkout widget
- [ ] Pacote tipográfico (Inter + size scale).

#### Borrador final del formulario V2 (3h)

- [ ] Revisar borrador V1.
- [ ] Refinar pregunta 6 (la más crítica).
- [ ] Validar respuestas con cifras realistas.
- [ ] Anotar lo pendiente (RIF, nombre final, URLs).

### Entregables fin de día 2
- Backend FastAPI funcionando localmente con flujo end-to-end probado.
- Migraciones Alembic exitosas.
- Pitch deck V1 (12 slides).
- Identidad visual final.

---

## Día 3 — Lunes 12 de mayo — Deploy + Dashboard skeleton

**Objetivo**: tener el backend en producción y el dashboard navegable conectado a la API real.

### Roberto (12h)

#### Bloque mañana (3h): Deploy backend

- [ ] Deploy en Railway con dominio personalizado (`api.pasarela.dev` o subdominio Railway si aún no hay dominio).
- [ ] Postgres provisionado en Railway o Supabase.
- [ ] Variables de entorno configuradas (todas las del `.env.example`).
- [ ] Migraciones aplicadas en producción.
- [ ] Smoke test: probar todos los endpoints en producción con cURL.
- [ ] Sentry configurado con DSN real.
- [ ] Healthcheck endpoint `GET /health`.

#### Bloque mediodía (5h): Dashboard setup + páginas core

- [ ] `cd apps/dashboard && npx create-next-app@latest` (Next.js 15 + TypeScript + Tailwind + App Router).
- [ ] Instalar shadcn/ui CLI + componentes base.
- [ ] Aplicar paleta de colores y tipografía del co-founder.
- [ ] Página `/login` con Supabase Auth (email/password).
- [ ] Layout autenticado con sidebar + header.
- [ ] Página `/dashboard` con cards de métricas (consume API real).
- [ ] Página `/dashboard/payments` con tabla de transacciones (consume `GET /v1/payments`).

#### Bloque tarde (4h): Páginas restantes + seed data

- [ ] Página `/dashboard/payments/[id]` con detalle + timeline de eventos.
- [ ] Página `/dashboard/api-keys` (generar/revocar/copiar).
- [ ] Página `/dashboard/webhooks` (CRUD de endpoints).
- [ ] Script Python para generar 50-80 transacciones falsas con timestamps realistas.
- [ ] Deploy del dashboard en Vercel.

### Co-founder (12h)

#### Redes sociales y copy (6h)

- [ ] Instagram: foto perfil, bio profesional, 2-3 posts iniciales (problema, solución, equipo).
- [ ] LinkedIn: página de empresa, bio, 1 post de lanzamiento de proyecto.
- [ ] Copy completo de la landing page (Hero, problema, solución, features, pricing, FAQ, footer).
- [ ] Copy de los 3-5 posts iniciales para cada red social.

#### Refinamiento pitch deck V2 (4h)

- [ ] Iterar slides con feedback Día 2.
- [ ] Mejorar visualmente con elementos de la identidad visual.
- [ ] Agregar screenshots reales del dashboard (Roberto los compartirá).

#### Investigación regulatoria profunda (2h)

- [ ] Leer texto completo (si disponible) de la Resolución BCV sobre Pago Móvil.
- [ ] Documentar referencias específicas en `docs/regulatory/`.
- [ ] Identificar potenciales preguntas que el jurado puede hacer sobre regulación.

### Entregables fin de día 3
- API pública funcionando en internet (Railway).
- Dashboard navegable con datos seed.
- Redes sociales creadas con contenido inicial.
- Pitch deck V2.

---

## Día 4 — Martes 13 de mayo — Checkout SDK + Tienda demo

**Objetivo**: tener el flujo end-to-end completamente funcional con widget embebible + tienda de demostración.

### Roberto (12h)

#### Bloque mañana (5h): Checkout Widget

- [ ] `cd apps/checkout-sdk && npm create vite@latest` con TypeScript.
- [ ] Configurar Vite en modo library (output: ES module + UMD).
- [ ] Widget self-contained con shadow DOM o estilos inline (no contaminar el sitio host).
- [ ] Modal de 3 pasos:
  1. Datos del cliente (teléfono, cédula, banco dropdown).
  2. Instrucciones para solicitar OTP (varían por banco).
  3. Input de OTP + confirmación.
- [ ] Estados visuales: loading spinner, success ✓, error ×.
- [ ] Build → un solo `checkout.js` minificado < 50KB.
- [ ] Hostear en Vercel (`/public/checkout.js`).

#### Bloque mediodía (4h): Tienda demo

- [ ] `cd apps/store-demo && npx create-next-app@latest`.
- [ ] 3 productos venezolanos creíbles con imágenes de Unsplash.
- [ ] Carrito en localStorage.
- [ ] Checkout page que invoca el widget.
- [ ] Backend del e-commerce (API routes de Next.js) que llama a Pasarela API.
- [ ] Recibe webhook y actualiza orden.
- [ ] Deploy en Vercel.

#### Bloque tarde (3h): QA integral

- [ ] Probar flujo completo 10 veces seguidas.
- [ ] Anotar bugs en lista.
- [ ] Arreglar los críticos (los cosméticos van al Día 5).
- [ ] Verificar webhooks llegando correctamente.
- [ ] Verificar dashboard se actualiza en tiempo real (refresh manual está OK).

### Co-founder (12h)

#### Marco regulatorio formal (4h)

- [ ] Crear documento `docs/regulatory/compliance-fase1.md` con el plan KYC/AML básico de comerciantes.
- [ ] Lista de verificaciones específicas que haremos antes de onboardear un comerciante.

#### One-pager y materiales escritos (4h)

- [ ] One-pager PDF (1 página, exportar del pitch deck).
- [ ] Bio del equipo (200-300 palabras cada uno).
- [ ] FAQ para el jurado: 10 preguntas frecuentes con respuestas listas.

#### Posts redes sociales (4h)

- [ ] Crear cronograma de 5-7 posts para esta semana.
- [ ] Diseñar imágenes en Canva con la identidad visual.
- [ ] Programar publicación.

### Entregables fin de día 4
- Flujo end-to-end completamente funcional en producción.
- Tienda demo con productos reales.
- One-pager PDF + bios + FAQ.

---

## Día 5 — Miércoles 14 de mayo — Landing + Nombre + Pulido visual

**Objetivo**: tener el producto "se ve como una empresa real" + decisión final de nombre.

### Roberto (12h)

#### Bloque mañana (4h): Decisión de nombre + dominio

- [ ] Roberto + co-founder deciden nombre final entre los 10 candidatos del Día 1.
- [ ] Comprar dominio en Namecheap/Porkbun.
- [ ] Configurar DNS en Cloudflare.
- [ ] Configurar subdominios:
  - `pasarela.dev` (o nombre real) → landing
  - `app.pasarela.dev` → dashboard
  - `api.pasarela.dev` → backend Railway
  - `tienda.pasarela.dev` → tienda demo
  - `cdn.pasarela.dev` → checkout widget
  - `docs.pasarela.dev` → documentación pública (Día 6)
- [ ] Actualizar URLs en todos los proyectos.
- [ ] Redeploys.

#### Bloque mediodía (5h): Landing page

- [ ] Estructura (mismo proyecto Next.js que el dashboard, rutas públicas):
  - Hero con propuesta de valor + CTAs.
  - Logos de tecnologías/bancos (Bancaribe destacado).
  - 3 features destacados con íconos.
  - Bloque de código mostrando la simplicidad de la integración.
  - Sección "Cómo funciona" con flujo visual.
  - Pricing transparente (revenue share Fase 1, "free to start").
  - FAQ.
  - Form de waitlist (Resend).
  - Footer con links a docs, GitHub, contacto, redes.

#### Bloque tarde (3h): Pulido visual general

- [ ] Animaciones sutiles (Framer Motion en transiciones clave).
- [ ] Favicons, meta tags, OG image (preview cuando se comparta el link).
- [ ] Modo oscuro en dashboard (shadcn lo da gratis).
- [ ] Pulido del widget de checkout.
- [ ] Estados vacíos bonitos.

### Co-founder (12h)

#### Pitch deck final V3 (5h)

- [ ] Iteración final con nombre real, screenshots reales, dominios reales.
- [ ] Exportar versión PDF de alta calidad.
- [ ] Versión web embebible (link Pitch.com público).

#### Apoyo en copy de landing (3h)

- [ ] Revisar copy de la landing implementada.
- [ ] Ajustes finos de mensaje.
- [ ] Asegurar consistencia con pitch deck.

#### Materiales post-aplicación (4h)

- [ ] Preparar paquete que se enviará a Bancaribe el día de la aplicación:
  - Carpeta drive con: pitch deck PDF, one-pager, video demo (Día 7), link al repo, link al deploy.
  - Email template para enviar a contactos de Bancaribe (postLaunch).

### Entregables fin de día 5
- Nombre y dominio final aplicado en todo.
- Landing page profesional deployada.
- Pitch deck final V3.

---

## Día 6 — Jueves 15 de mayo — Documentación pública + Pulido

**Objetivo**: docs.pasarela.dev en línea + producto pulido al máximo.

### Roberto (12h)

#### Bloque mañana (5h): Documentación pública

- [ ] Página `/docs` en Next.js (rutas estáticas, generadas de Markdown).
- [ ] Páginas:
  - `/docs/quickstart` (5 minutos)
  - `/docs/api-reference/payments`
  - `/docs/api-reference/webhooks`
  - `/docs/api-reference/api-keys`
  - `/docs/sdks/javascript`
  - `/docs/webhooks/signature-verification`
- [ ] Code blocks con sintaxis highlighting (Shiki o Prism).
- [ ] Ejemplos en JavaScript, Python, cURL.
- [ ] Deploy en `docs.pasarela.dev`.

#### Bloque mediodía (4h): Pulido visual final

- [ ] Performance: Lighthouse > 85 en landing y dashboard.
- [ ] Mobile responsiveness verificado.
- [ ] Errores en consola: 0.
- [ ] Loading states en todas las páginas asíncronas.
- [ ] Empty states bonitos.
- [ ] Toast notifications en acciones clave.

#### Bloque tarde (3h): Demo data + casos límite

- [ ] Generar 200+ transacciones seed con variedad realista (montos, estados, fechas).
- [ ] Crear 3 merchants de prueba con datos completos.
- [ ] Probar QA exhaustivo: navegadores, devices, conexiones lentas.

### Co-founder (12h)

#### Video demo (6h)

- [ ] Escribir script de 90 segundos.
- [ ] Ensayar 3-4 veces antes de grabar.
- [ ] Grabar con Loom o ScreenStudio (audio claro, pantalla a 1080p mínimo).
- [ ] Hacer 5-6 takes y elegir el mejor.
- [ ] Edición mínima (no perfeccionar): cortes, transiciones simples.
- [ ] Subir a YouTube unlisted + embedded en landing.

#### Preparación del pitch oral (4h)

- [ ] Practicar pitch de 5 minutos basado en deck.
- [ ] Anticipar 15 preguntas del jurado y preparar respuestas:
  - "¿Qué los diferencia de Megasoft/Yipi?"
  - "¿Por qué los comerciantes los preferirían?"
  - "¿Qué necesitan de Bancaribe?"
  - "¿Cómo cumplen LC/FT/FPADM?"
  - "¿No quedan dependientes de Bancaribe?"
  - "¿Cuánto tiempo hasta breakeven?"
  - "¿Qué pasa si Bancaribe construye esto in-house?"
  - "¿Han hablado con comerciantes reales?"
  - "¿Cuánto les costaría operar mes a mes?"
  - "¿Quién más invierte/apoya el proyecto?"
  - etc.
- [ ] Documentar respuestas en `docs/pitch/qa-jurado.md`.

#### Cronograma de publicación post-aplicación (2h)

- [ ] Plan de posts para el día del envío + siguientes 2 semanas.
- [ ] Mensajes preparados para contactar comerciantes interesados (post-aplicación).

### Entregables fin de día 6
- docs.pasarela.dev en línea.
- Video demo grabado y publicado.
- Q&A del jurado documentado.

---

## Día 7 — Viernes 16 de mayo — QA final + Envío + Buffer

**Objetivo**: aplicación enviada.

### Roberto (12h)

#### Bloque mañana (4h): QA brutal final

- [ ] Probar todo el flujo end-to-end 20 veces en distintos navegadores (Chrome, Firefox, Safari, Edge, móvil iOS, móvil Android).
- [ ] Probar con conexión lenta (DevTools Slow 3G).
- [ ] Verificar todos los enlaces de landing, dashboard, docs.
- [ ] Verificar formularios funcionan (waitlist, login, etc.).
- [ ] Stress test mínimo: 50 requests/seg en endpoint de payments → debe responder OK.

#### Bloque mediodía (4h): Buffer para fixes críticos

- [ ] Tiempo reservado para bugs que aparezcan en QA.
- [ ] Cualquier ajuste de última hora pedido por el co-founder.

#### Bloque tarde (4h): Acompañamiento al envío

- [ ] Revisión cruzada del formulario con el co-founder.
- [ ] Confirmación de todas las URLs funcionando.
- [ ] Asistir al co-founder en el envío del formulario.
- [ ] Captura de pantalla de confirmación de envío.

### Co-founder (12h)

#### Bloque mañana (3h): Refinamiento final del formulario

- [ ] Revisión última del borrador con todos los datos reales actualizados.
- [ ] Lectura en voz alta de cada respuesta (catch typos).
- [ ] Verificar que el RIF, emails, URLs sean correctos.

#### Bloque mediodía (3h): Envío del formulario

- [ ] Llenar el formulario oficial de Microsoft Forms.
- [ ] Pegar cada respuesta y verificar formato.
- [ ] Hacer submit.
- [ ] Captura de pantalla de confirmación.
- [ ] Backup de las respuestas en PDF.

#### Bloque tarde (6h): Post-envío

- [ ] Publicar en redes sociales: "Aplicamos a Shark Bank Bancaribe".
- [ ] Email a contactos personales que puedan amplificar.
- [ ] Iniciar conversaciones con potenciales early adopters.
- [ ] Documentar el proceso del concurso para retrospectiva interna.

### Entregables fin de día 7
- **APLICACIÓN ENVIADA**.
- Captura de confirmación.
- Anuncio público.

---

## Día 8 — Sábado 17 de mayo — Buffer / Descanso

**Objetivo**: respirar, descansar, y comenzar siguiente fase.

### Si todo salió bien (lo esperado)

- Descanso completo. La semana fue intensa.
- Reflexión y retrospectiva del proceso.
- Comenzar planificación de "post-aplicación":
  - Estrategia mientras esperamos respuesta de Bancaribe.
  - Desarrollo continuo del producto.
  - Contactos paralelos con otros bancos como plan B.

### Si quedó algo pendiente

- Usar este día como buffer absoluto.
- El cierre del concurso es hoy a la hora indicada — verificar plazo exacto.

---

## Después de la semana

Una vez enviada la aplicación:

1. **Esperar respuesta** (Bancaribe indicará timeline de preselección).
2. **Continuar desarrollo** mientras esperamos.
3. **Buscar primeros 3-5 comerciantes piloto** dispuestos a probar gratis incluso sin partnership formal.
4. **Aplicar a otros concursos** en paralelo (plan B).
5. **Refinar producto** basándose en feedback inicial.
6. **Preparar Demo Day** por si quedamos seleccionados.

---

## Reglas finales

1. **Si surge algo no previsto** → consultarlo en standup matutino, no entrar en pánico.
2. **Si nos atrasamos un día** → recortar features cosméticos, no esenciales.
3. **Si nos enfermamos** → la salud va primero. Mejor enviar Día 8 con buena salud que Día 7 enfermos.
4. **Si Bancaribe extiende el plazo** → nosotros no extendemos. Enviamos cuando esté listo, no procrastinamos.
5. **Si algo falla espectacularmente** → recordar que esto es un MVP, no el producto final. El concurso pide PMV, no perfección.
