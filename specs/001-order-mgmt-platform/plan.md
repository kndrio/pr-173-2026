# Implementation Plan: Order Management Platform MVP

**Branch**: `001-order-mgmt-platform` | **Date**: 2026-03-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-order-mgmt-platform/spec.md`

---

## Summary

Plataforma interna de gestão de pedidos para substituir controle por planilhas. Implementada como monorepo com dois microserviços FastAPI (auth-service + orders-service), dois microfrontends React/Vite (shell + orders-mfe) orquestrados via Module Federation, PostgreSQL como banco relacional (databases separados por serviço), e Redis para cache de listagens e Pub/Sub de eventos. Análise de pedidos via Anthropic Claude API com fallback baseado em regras.

---

## Technical Context

**Language/Version**: Python 3.11 (backend) | TypeScript 5.x strict mode (frontend) | Node.js 20 LTS
**Primary Dependencies**:
- Backend: FastAPI ≥ 0.100, SQLAlchemy 2.0 (async), Alembic, python-jose, passlib[bcrypt], structlog, asyncpg, redis[hiredis], httpx, pydantic-settings
- Frontend: React 18, Vite 5, @originjs/vite-plugin-federation, Zustand, TanStack Query v5, React Hook Form, Zod, React Router v6
- Infra: Docker Compose, NGINX (reverse proxy + static files), GitHub Actions

**Storage**: PostgreSQL 16 (1 container, 2 databases: `auth_db` e `orders_db`) + Redis 7 (cache TTL + Pub/Sub)
**Testing**: pytest + pytest-asyncio (backend) | React Testing Library + Vitest (frontend)
**Target Platform**: Linux containers (Docker Compose), desenvolvimento em qualquer OS com Docker
**Project Type**: Web application — monorepo com microserviços backend + microfrontends
**Performance Goals**: Listagem de pedidos < 2s | Análise IA < 10s | Startup completo < 5min
**Constraints**: `docker compose up` funcional; sem dependências de runtime local; sem secrets em código
**Scale/Scope**: MVP para demonstração — suporte a centenas de pedidos, dezenas de usuários

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Arquitetura | 2 backend services (auth + orders) com databases separados; 2 MFEs independentes (shell + orders-mfe) | ✅ |
| II. Stack Backend | Python 3.11/FastAPI ≥ 0.100/PostgreSQL 16 + Alembic migrations | ✅ |
| III. Stack Frontend | React/TypeScript strict ≥ 5.0/Vite; `any` proibido sem justificativa | ✅ |
| IV. Infraestrutura | Multi-stage Dockerfiles (python:3.11-slim, node:20-alpine); non-root user; `docker compose up` funcional | ✅ |
| V. Qualidade | type hints completos + mypy; Ruff lint; pytest; ESLint + tsc --noEmit; RTL | ✅ |
| VI. Segurança | JWT shared secret via env var; Pydantic + Zod em todas as camadas; `.env.example` documentado; LGPD (coleta mínima) | ✅ |
| VII. Observabilidade | structlog JSON com X-Request-ID; `/health` em ambos os serviços; campos obrigatórios: service, level, timestamp, request_id | ✅ |
| VIII. Pragmatismo | Fallback documentado para Module Federation; MFE fallback = NGINX com apps independentes (ADR-003) | ✅ |
| IX. Documentação | README com diagrama de arquitetura; ADRs em docs/adr/; Swagger automático via FastAPI | ✅ |
| X. IA como Método | SDD via SpecKit — spec → código; uso de IA documentado no README | ✅ |

**Resultado**: Todos os gates aprovados. Nenhuma violação que requeira justificativa em Complexity Tracking.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-order-mgmt-platform/
├── plan.md              # Este arquivo (/speckit.plan)
├── research.md          # Decisões e rationale (Phase 0)
├── data-model.md        # Entidades, relacionamentos, schemas (Phase 1)
├── quickstart.md        # Getting started guide (Phase 1)
├── contracts/           # API contracts por serviço (Phase 1)
│   ├── auth-service.md
│   └── orders-service.md
├── checklists/
│   └── requirements.md  # Checklist de qualidade da spec
└── tasks.md             # Phase 2 output (/speckit.tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
pedidos-platform/
├── docker-compose.yml
├── .env.example
├── README.md
├── .github/
│   └── workflows/
│       ├── auth-service.yml      # CI paralelo: lint + mypy + pytest + build
│       ├── orders-service.yml    # CI paralelo: lint + mypy + pytest + build
│       └── frontend.yml          # CI paralelo: eslint + tsc + vitest + build
├── services/
│   ├── auth-service/
│   │   ├── Dockerfile            # Multi-stage: builder → python:3.11-slim
│   │   ├── requirements.txt
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   ├── app/
│   │   │   ├── main.py           # FastAPI app, CORS, structlog middleware, /health
│   │   │   ├── core/
│   │   │   │   ├── config.py     # pydantic-settings (JWT_SECRET, DATABASE_URL, etc.)
│   │   │   │   ├── security.py   # JWT encode/decode + bcrypt hash/verify
│   │   │   │   ├── database.py   # AsyncEngine + async_session_factory
│   │   │   │   └── logging.py    # structlog configuration
│   │   │   ├── models/
│   │   │   │   └── user.py       # SQLAlchemy User (id, full_name, email, hashed_password, role, is_active)
│   │   │   ├── schemas/
│   │   │   │   └── user.py       # UserCreate, UserLogin, UserResponse, TokenResponse, UserListResponse
│   │   │   ├── dependencies.py   # get_db, get_current_user
│   │   │   └── api/
│   │   │       └── v1/
│   │   │           ├── router.py
│   │   │           └── endpoints/
│   │   │               ├── auth.py    # POST /register, POST /login
│   │   │               └── users.py  # GET /me, GET /users
│   │   └── tests/
│   │       ├── conftest.py
│   │       ├── test_auth.py       # register, login, validações, duplicatas
│   │       └── test_users.py      # me, listagem, paginação
│   └── orders-service/
│       ├── Dockerfile             # Multi-stage: builder → python:3.11-slim
│       ├── requirements.txt
│       ├── alembic.ini
│       ├── alembic/
│       │   ├── env.py
│       │   └── versions/
│       ├── app/
│       │   ├── main.py            # FastAPI app, CORS, middleware, /health (+ redis status)
│       │   ├── core/
│       │   │   ├── config.py      # Settings (JWT_SECRET, DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY)
│       │   │   ├── database.py    # AsyncEngine + session factory (orders_db)
│       │   │   ├── redis.py       # Redis client factory (cache + pubsub)
│       │   │   └── logging.py
│       │   ├── models/
│       │   │   └── order.py       # Order + OrderItem SQLAlchemy models
│       │   ├── schemas/
│       │   │   └── order.py       # OrderCreate, OrderResponse, OrderListResponse, OrderStatusUpdate, AIAnalysisResponse
│       │   ├── dependencies.py    # get_db, get_redis, get_current_user (JWT validation)
│       │   └── api/
│       │       └── v1/
│       │           ├── router.py
│       │           └── endpoints/
│       │               └── orders.py  # CRUD + status PATCH + analyze POST
│       ├── services/
│       │   ├── order_service.py   # Lógica: create, list (cache-aware), get, update_status (validação transição)
│       │   ├── cache_service.py   # Redis get/set/invalidate (SCAN + DEL pattern orders:list:*)
│       │   ├── event_service.py   # Redis publish(channel="orders", message=OrderEvent)
│       │   └── ai_service.py      # analyze_order: Claude API call + rule-based fallback
│       └── tests/
│           ├── conftest.py
│           ├── test_orders.py     # CRUD, transições válidas/inválidas, cálculo total
│           └── test_ai_service.py # Análise com mock da API + fallback
├── frontend/
│   ├── shell/
│   │   ├── Dockerfile             # Multi-stage: node:20-alpine builder → nginx:alpine
│   │   ├── nginx.conf             # Proxy /api/auth → auth:8001, /api/orders → orders:8002; serve MFEs
│   │   ├── package.json
│   │   ├── vite.config.ts         # Module Federation host config
│   │   ├── tsconfig.json          # strict: true
│   │   └── src/
│   │       ├── main.tsx
│   │       ├── App.tsx            # React Router + ProtectedRoute + lazy load MFE
│   │       ├── store/
│   │       │   └── authStore.ts   # Zustand: token (memória), user, login/logout actions
│   │       ├── services/
│   │       │   └── authApi.ts     # axios/fetch calls → /api/auth
│   │       ├── components/
│   │       │   ├── Layout.tsx     # Header + Sidebar + Outlet
│   │       │   ├── Header.tsx     # Logo, nome usuário, logout
│   │       │   ├── Sidebar.tsx    # Navegação lateral (Pedidos, Usuários)
│   │       │   └── ProtectedRoute.tsx
│   │       └── pages/
│   │           ├── LoginPage.tsx
│   │           ├── RegisterPage.tsx
│   │           └── NotFoundPage.tsx
│   └── orders-mfe/
│       ├── Dockerfile             # Multi-stage: node:20-alpine builder → nginx:alpine
│       ├── package.json
│       ├── vite.config.ts         # Module Federation remote config; expõe OrdersApp
│       ├── tsconfig.json          # strict: true
│       └── src/
│           ├── main.tsx           # Bootstrap standalone + remote entry
│           ├── App.tsx            # React Router interno do MFE
│           ├── types/
│           │   └── order.ts       # Order, OrderItem, Priority, Status types (TypeScript)
│           ├── services/
│           │   └── ordersApi.ts   # TanStack Query fetchers → /api/orders
│           ├── hooks/
│           │   ├── useOrders.ts   # useQuery (listagem com filtros + paginação)
│           │   ├── useOrderDetail.ts # useQuery (pedido por ID)
│           │   ├── useCreateOrder.ts # useMutation (criação)
│           │   └── useUpdateStatus.ts # useMutation (status PATCH)
│           └── components/
│               ├── OrderList.tsx       # Tabela/cards responsiva
│               ├── OrderCard.tsx       # Card individual (mobile)
│               ├── OrderForm.tsx       # React Hook Form + Zod + itens dinâmicos
│               ├── OrderDetail.tsx     # Detalhe completo
│               ├── StatusBadge.tsx     # Badge colorido por status
│               ├── StatusActions.tsx   # Botões de transição válidos por status atual
│               ├── AIAnalysis.tsx      # Botão + loading + resultado análise
│               ├── FilterBar.tsx       # Selects de status + prioridade + contadores
│               └── Pagination.tsx      # Controle de paginação
└── docs/
    └── adr/
        ├── 001-fastapi-choice.md         # FastAPI vs Django vs Flask
        ├── 002-redis-dual-purpose.md     # Redis para cache + Pub/Sub
        ├── 003-module-federation-strategy.md  # MF primário + fallback NGINX
        └── 004-postgresql-single-instance.md  # 1 container, 2 databases
```

**Structure Decision**: Monorepo com separação clara entre `services/` (backend Python) e `frontend/` (MFEs TypeScript). O `docker-compose.yml` na raiz orquestra todos os 6+ serviços (postgres, redis, auth-service, orders-service, shell, orders-mfe). Sem ferramentas de monorepo adicionais — `docker compose` é o orquestrador único.

---

## Implementation Phases

### Phase 0: Research ✅ (completo)

Ver [research.md](research.md) para:
- Estratégia Module Federation + fallback
- JWT shared secret pattern
- Redis cache TTL e invalidação
- Claude API + fallback rule-based
- SQLAlchemy async session management
- Estrutura monorepo
- structlog + correlation ID

### Phase 1: Design & Contracts ✅ (completo)

| Artefato | Arquivo | Status |
|----------|---------|--------|
| Modelo de dados | [data-model.md](data-model.md) | ✅ |
| Contrato Auth API | [contracts/auth-service.md](contracts/auth-service.md) | ✅ |
| Contrato Orders API | [contracts/orders-service.md](contracts/orders-service.md) | ✅ |
| Guia de setup | [quickstart.md](quickstart.md) | ✅ |

### Phase 2: Tasks (próxima etapa)

Executar `/speckit.tasks` para gerar `tasks.md` com o breakdown de implementação por user story.

---

## Implementation Order (por User Story)

Seguindo a constituição (Princípio VIII — Pragmatismo: profundidade antes de amplitude):

| Ordem | User Story | Prioridade | Dependências |
|-------|-----------|------------|--------------|
| 1 | Auth: registro + login + JWT | P1 | PostgreSQL, migrations |
| 2 | Auth: endpoint /me + listagem usuários | P1 | US-1 |
| 3 | Orders: criação de pedido + cálculo total | P1 | PostgreSQL, US-1 (JWT) |
| 4 | Orders: listagem + filtros + paginação + cache | P2 | US-3 |
| 5 | Orders: detalhe por ID + atualização de status | P2 | US-3 |
| 6 | Frontend Shell: layout + auth flow + routing | P1 | US-1, US-2 |
| 7 | Frontend Orders MFE: listagem + filtros | P2 | US-4, Shell |
| 8 | Frontend Orders MFE: formulário criação | P1 | US-3, Shell |
| 9 | Frontend Orders MFE: detalhe + ações de status | P2 | US-5, Shell |
| 10 | Orders: endpoint análise IA + fallback | P3 | US-3 |
| 11 | Frontend: componente análise IA | P3 | US-10, Shell |
| 12 | Infrastructure: docker-compose + CI + seed | P1 | Todos |
| 13 | Documentation: README + ADRs + diagrama | P3 | Todos |

---

## Key Technical Decisions (Resumo)

| Decisão | Escolha | Alternativa Rejeitada |
|---------|---------|----------------------|
| Auth pattern | JWT HS256 shared secret | RS256 PKI (overhead desnecessário no MVP) |
| Redis usage | Cache TTL 5min + Pub/Sub (mesmo container) | Dois serviços separados |
| MFE strategy | Module Federation (@originjs/vite-plugin-federation) | single-spa, iframes |
| MFE fallback | NGINX routing com apps independentes | Sem fallback |
| DB isolation | 1 container PostgreSQL, 2 databases lógicos | 2 containers separados |
| IA integration | httpx async + fallback rules | Só regras (sem IA) |
| Cache invalidation | Delete-on-write (SCAN+DEL) + TTL safety net | Write-through, TTL longo |
| State frontend | Zustand (auth, memória) + TanStack Query (server state) | Redux, Context API |
