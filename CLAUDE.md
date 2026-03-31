# Pedidos Platform — Development Guidelines

Auto-generated from feature plan `001-order-mgmt-platform`. Last updated: 2026-03-30

## Active Technologies

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend language | Python | 3.11+ |
| Backend framework | FastAPI | ≥ 0.100 |
| ORM | SQLAlchemy (async) | 2.0 |
| Migrations | Alembic | latest |
| Auth | python-jose (JWT) + passlib[bcrypt] | latest |
| Validation (backend) | Pydantic v2 | latest |
| Logging | structlog | latest |
| HTTP client (IA) | httpx | latest |
| Database | PostgreSQL | 16 |
| Cache + Events | Redis | 7 |
| Frontend language | TypeScript | ≥ 5.0 (strict mode) |
| Frontend framework | React | 18 |
| Build tool | Vite | 5 |
| MFE strategy | @originjs/vite-plugin-federation | latest |
| State (client) | Zustand | latest |
| State (server) | TanStack Query | v5 |
| Forms | React Hook Form + Zod | latest |
| Linting (Python) | Ruff + mypy | latest |
| Linting (TS) | ESLint + tsc --noEmit | latest |
| Testing (backend) | pytest + pytest-asyncio | latest |
| Testing (frontend) | Vitest + React Testing Library | latest |
| Containerization | Docker Compose | v2 |
| CI | GitHub Actions | — |
| AI API | Anthropic Claude (claude-sonnet-4-20250514) | — |

## Project Structure

```text
pedidos-platform/
├── docker-compose.yml
├── .env.example
├── CLAUDE.md                   # Este arquivo
├── README.md
├── .github/workflows/
│   ├── auth-service.yml
│   ├── orders-service.yml
│   └── frontend.yml
├── services/
│   ├── auth-service/           # FastAPI, porta 8001, banco auth_db
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic/
│   │   └── app/
│   │       ├── main.py
│   │       ├── core/           # config, security, database, logging
│   │       ├── models/         # SQLAlchemy models
│   │       ├── schemas/        # Pydantic schemas
│   │       ├── dependencies.py
│   │       └── api/v1/endpoints/
│   └── orders-service/         # FastAPI, porta 8002, banco orders_db
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── alembic/
│       ├── app/
│       │   ├── main.py
│       │   ├── core/           # config, database, redis, logging
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── dependencies.py
│       │   └── api/v1/endpoints/
│       └── services/           # order_service, cache_service, event_service, ai_service
├── frontend/
│   ├── shell/                  # MFE Host, porta 3000
│   │   ├── Dockerfile
│   │   ├── nginx.conf
│   │   └── src/
│   │       ├── store/authStore.ts   # Zustand — token em memória
│   │       ├── components/          # Layout, Header, Sidebar, ProtectedRoute
│   │       └── pages/              # LoginPage, RegisterPage
│   └── orders-mfe/             # MFE Remote, porta 3001
│       ├── Dockerfile
│       └── src/
│           ├── types/order.ts
│           ├── services/ordersApi.ts
│           ├── hooks/               # useOrders, useOrderDetail, useCreateOrder, useUpdateStatus
│           └── components/         # OrderList, OrderForm, OrderDetail, StatusBadge, AIAnalysis, FilterBar
└── docs/adr/                   # Architecture Decision Records
```

## Commands

### Stack completa
```bash
docker compose up --build      # Primeira vez
docker compose up              # Subsequente
docker compose down            # Parar
docker compose logs -f <svc>  # Logs
```

### Testes
```bash
# Backend
docker compose run --rm auth-service pytest tests/ -v
docker compose run --rm orders-service pytest tests/ -v

# Frontend
docker compose run --rm shell vitest run
docker compose run --rm orders-mfe vitest run
```

### Qualidade
```bash
# Python
docker compose run --rm auth-service ruff check app/
docker compose run --rm auth-service mypy app/

# TypeScript
docker compose run --rm shell tsc --noEmit
docker compose run --rm shell eslint src/
```

### Migrations
```bash
docker compose run --rm auth-service alembic revision --autogenerate -m "description"
docker compose run --rm auth-service alembic upgrade head
docker compose run --rm orders-service alembic revision --autogenerate -m "description"
docker compose run --rm orders-service alembic upgrade head
```

## Code Style

### Python (Ruff + mypy)
- Type hints obrigatórios em todas as funções e métodos
- Sem `type: ignore` sem comentário justificando
- Docstrings apenas em código público de biblioteca (não em endpoints internos)
- Imports organizados: stdlib → third-party → local
- `async def` para todos os endpoints e operações de I/O

### TypeScript (strict mode)
- `any` proibido sem comentário `// eslint-disable-next-line @typescript-eslint/no-explicit-any` e justificativa
- Interfaces para tipos de dados; `type` para unions e aliases
- Componentes React com tipagem explícita de props
- Hooks TanStack Query para todo estado de servidor (sem fetch manual em componentes)

### Segurança (obrigatório)
- Secrets NUNCA em código — sempre via `.env` (não versionado)
- JWT validado em todo endpoint protegido via `get_current_user` dependency
- Validação Pydantic no backend + Zod no frontend para toda entrada de usuário
- `CORS` configurado explicitamente — sem `allow_origins=["*"]` em produção

### Observabilidade (obrigatório)
- Todo request recebe `X-Request-ID` (gerado se ausente)
- Logs via `structlog` — sem `print()` em código de produção
- Campos obrigatórios em todo log: `service`, `level`, `timestamp`, `request_id`
- `/health` deve responder 200 com status do banco e Redis

## Constitution Gates (Quality Gates antes de merge)

- [ ] `ruff check .` sem erros (Python)
- [ ] `mypy` sem erros em todos os serviços backend
- [ ] `eslint .` sem erros (TypeScript)
- [ ] `tsc --noEmit` sem erros em todos os MFEs
- [ ] `pytest` passando (backend)
- [ ] Vitest + RTL passando (frontend)
- [ ] `docker compose build` bem-sucedido
- [ ] `docker compose up` inicia stack sem erros
- [ ] `GET /health` responde 200 em ambos os serviços
- [ ] Sem secrets em texto plano no código

## Recent Changes

- `001-order-mgmt-platform` (2026-03-30): Setup inicial do projeto — toda a stack de gestão de pedidos incluindo auth-service, orders-service, shell MFE e orders MFE. Análise de pedidos via Claude API com fallback por regras.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
