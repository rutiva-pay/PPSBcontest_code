# Pasarela — Pagos developer-first para el e-commerce venezolano

> **Estado**: Prototipo funcional en construcción · **Aplicación**: Shark Bank Bancaribe 2026

Pasarela es la capa developer-experience que multiplica la adopción del Open Banking de Bancaribe en el segmento SMB venezolano. Construimos el SDK, dashboard y checkout que faltan para que cualquier desarrollador pueda integrar pagos C2P en una tienda online en menos de 10 minutos.

---

## ¿Qué problema resolvemos?

Bancaribe ya construyó 8 APIs robustas en su Open Banking (C2P2, B2P, Transferencia Inmediata, etc.) que técnicamente igualan a las mejores pasarelas globales. Pero el segmento SMB (pequeños y medianos e-commerces) no las adopta porque:

- La documentación requiere login y no es pública
- No hay sandbox abierto para experimentar
- Los SDKs solo están disponibles en Java y Android
- El onboarding es 100% manual (vía email a `mdpagos@bancaribe.com.ve`)
- No existen plugins listos para WooCommerce, Shopify, PrestaShop

Mientras tanto, Stripe construyó un imperio de $90B en 14 años basándose en una sola cosa: developer-experience. Nosotros traemos esa filosofía al ecosistema venezolano.

---

## Nuestra visión en tres fases

### Fase 1 (Mes 0-12): Facilitador C2P sobre Bancaribe
Operamos como pasarela tecnológica pura. Comerciantes con cuenta jurídica en Bancaribe acceden a la mejor experiencia de pagos del mercado. Funcionamos como **canal de adquisición de cuentas jurídicas** para Bancaribe.

### Fase 2 (Mes 12-24): Expansión multi-banco como facilitador
Integración con BNC, Mercantil y otros bancos principales mediante el mismo Bank Adapter Pattern. Bancaribe mantiene posición de founding partner.

### Fase 3 (Mes 24+): Modelo agregador apadrinado por Bancaribe
Bajo paraguas regulatorio de Bancaribe como sub-agente tecnológico, evolucionamos a manejo directo de fondos. Habilita productos avanzados: split payments, escrow, financiamiento basado en flujo, multi-divisa.

---

## Arquitectura del repo

```
pasarela/
├── apps/
│   ├── core-api/        # Backend FastAPI (Python 3.12)
│   ├── dashboard/       # Dashboard del comerciante (Next.js + shadcn)
│   ├── checkout-sdk/    # Widget JS embebible (Vite library mode)
│   └── store-demo/      # E-commerce demo para presentación
├── packages/
│   └── shared-types/    # Schemas compartidos
├── docs/
│   ├── architecture/    # Diagramas C4, decisiones arquitectónicas
│   ├── api/             # OpenAPI spec, ejemplos
│   ├── pitch/           # Pitch deck, one-pager, video script
│   ├── research/        # Investigación de mercado y Open Banking Bancaribe
│   └── regulatory/      # Marco regulatorio, KYC/AML, LC/FT/FPADM
└── infra/
    └── docker/          # Docker Compose para desarrollo local
```

---

## Stack tecnológico

**Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, PostgreSQL 16, Alembic
**Frontend**: Next.js 15, TypeScript, Tailwind, shadcn/ui
**Checkout SDK**: TypeScript, Vite (library mode)
**Infra**: Railway (backend), Vercel (frontend), Supabase (auth)
**Observabilidad**: Sentry, structured logging

---

## Documentación clave

- [Visión técnica](docs/architecture/01-vision-tecnica.md)
- [Arquitectura](docs/architecture/02-arquitectura.md)
- [Modelo de datos](docs/architecture/03-modelo-datos.md)
- [API Spec](docs/api/04-api-spec.md)
- [Flujo C2P](docs/architecture/05-flujo-c2p.md)
- [Seguridad](docs/architecture/06-seguridad.md)
- [Roadmap](docs/architecture/07-roadmap.md)
- [Marco regulatorio](docs/regulatory/08-marco-regulatorio.md)
- [Análisis de mercado](docs/research/09-mercado.md)

---

## Equipo

- **[Tu nombre]** — Engineering Lead
- **[Co-founder]** — Business & Design Lead

---

## Estado del proyecto

🚧 **En desarrollo activo** — aplicación a Shark Bank Bancaribe (cierre 17 de mayo 2026).

Este repo es público como demostración de transparencia y compromiso técnico. Cada commit es parte de la propuesta.
