# Quickstart: Order Management Platform MVP

**Branch**: `001-order-mgmt-platform` | **Date**: 2026-03-30

---

## Pré-requisitos

| Ferramenta | Versão Mínima | Verificar |
|------------|---------------|-----------|
| Docker | 24+ | `docker --version` |
| Docker Compose | 2.20+ | `docker compose version` |
| Git | qualquer | `git --version` |

> Sem necessidade de Python, Node.js, ou qualquer runtime local — tudo roda em containers.

---

## Setup em 3 Passos

### 1. Clonar e configurar variáveis de ambiente

```bash
git clone <repo-url> pedidos-platform
cd pedidos-platform
cp .env.example .env
```

Editar `.env` com valores reais:
```env
# Gerado automaticamente se deixado vazio no exemplo
JWT_SECRET=sua-chave-secreta-aqui-minimo-32-caracteres

# Anthropic (opcional — fallback por regras se ausente)
ANTHROPIC_API_KEY=sk-ant-...

# Banco de dados (padrão funciona com docker-compose)
POSTGRES_USER=pedidos
POSTGRES_PASSWORD=pedidos123
POSTGRES_HOST=postgres
```

### 2. Subir toda a stack

```bash
docker compose up --build
```

Aguardar todos os serviços ficarem healthy (~60-90 segundos no primeiro build).

### 3. Acessar a plataforma

| Serviço | URL |
|---------|-----|
| **Aplicação** (Shell MFE) | http://localhost:3000 |
| **API Auth** (Swagger) | http://localhost:8001/docs |
| **API Orders** (Swagger) | http://localhost:8002/docs |

> Dados de seed são carregados automaticamente na primeira inicialização.

---

## Credenciais de Demonstração

| Papel | Email | Senha |
|-------|-------|-------|
| Administrador | `admin@pedidos.dev` | `admin123!` |
| Gestor | `gestor@pedidos.dev` | `gestor123!` |
| Operador | `operador@pedidos.dev` | `operador123!` |

---

## Estrutura do Projeto

```
pedidos-platform/
├── docker-compose.yml          # Orquestração completa da stack
├── .env.example                # Template de variáveis de ambiente
├── .github/
│   └── workflows/
│       ├── auth-service.yml    # CI: lint + test + build do auth service
│       ├── orders-service.yml  # CI: lint + test + build do orders service
│       └── frontend.yml        # CI: lint + type-check + build dos MFEs
├── services/
│   ├── auth-service/
│   │   ├── Dockerfile          # Multi-stage build (python:3.11-slim)
│   │   ├── requirements.txt
│   │   ├── alembic/            # Migrations do banco auth_db
│   │   ├── app/
│   │   │   ├── main.py         # FastAPI app + middleware
│   │   │   ├── core/
│   │   │   │   ├── config.py   # Settings via pydantic-settings
│   │   │   │   ├── security.py # JWT encode/decode + bcrypt
│   │   │   │   └── database.py # SQLAlchemy async engine + session
│   │   │   ├── models/
│   │   │   │   └── user.py     # SQLAlchemy User model
│   │   │   ├── schemas/
│   │   │   │   └── user.py     # Pydantic request/response schemas
│   │   │   ├── api/v1/
│   │   │   │   └── endpoints/
│   │   │   │       ├── auth.py  # POST /register, POST /login
│   │   │   │       └── users.py # GET /me, GET /users
│   │   │   └── services/
│   │   │       └── user_service.py
│   │   └── tests/
│   │       ├── test_auth.py
│   │       └── test_users.py
│   └── orders-service/
│       ├── Dockerfile          # Multi-stage build (python:3.11-slim)
│       ├── requirements.txt
│       ├── alembic/            # Migrations do banco orders_db
│       ├── app/
│       │   ├── main.py         # FastAPI app + middleware
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   ├── database.py
│       │   │   └── redis.py    # Redis client (cache + pub/sub)
│       │   ├── models/
│       │   │   └── order.py    # Order + OrderItem models
│       │   ├── schemas/
│       │   │   └── order.py    # Pydantic schemas
│       │   ├── api/v1/
│       │   │   └── endpoints/
│       │   │       └── orders.py # CRUD + status + analyze
│       │   └── services/
│       │       ├── order_service.py   # Lógica de negócio + transições
│       │       ├── cache_service.py   # Redis cache (get/set/invalidate)
│       │       ├── event_service.py   # Redis Pub/Sub publisher
│       │       └── ai_service.py      # Claude API + fallback rules
│       └── tests/
│           ├── test_orders.py
│           └── test_ai_service.py
├── frontend/
│   ├── shell/
│   │   ├── Dockerfile          # Multi-stage (node:20-alpine + nginx:alpine)
│   │   ├── nginx.conf          # Reverse proxy + Module Federation
│   │   ├── package.json
│   │   ├── vite.config.ts      # @originjs/vite-plugin-federation (host)
│   │   ├── tsconfig.json       # strict mode
│   │   └── src/
│   │       ├── main.tsx
│   │       ├── App.tsx         # Router + layout
│   │       ├── store/
│   │       │   └── authStore.ts  # Zustand (token em memória)
│   │       ├── components/
│   │       │   ├── Layout.tsx
│   │       │   ├── Header.tsx
│   │       │   └── Sidebar.tsx
│   │       └── pages/
│   │           ├── LoginPage.tsx
│   │           ├── RegisterPage.tsx
│   │           └── HomePage.tsx
│   └── orders-mfe/
│       ├── Dockerfile          # Multi-stage (node:20-alpine + nginx:alpine)
│       ├── package.json
│       ├── vite.config.ts      # Module Federation (remote)
│       ├── tsconfig.json       # strict mode
│       └── src/
│           ├── main.tsx
│           ├── components/
│           │   ├── OrderList.tsx      # Tabela/cards com badges
│           │   ├── OrderCard.tsx      # Card individual
│           │   ├── OrderForm.tsx      # Formulário criação + itens dinâmicos
│           │   ├── OrderDetail.tsx    # Visão completa do pedido
│           │   ├── StatusBadge.tsx    # Badge colorido por status
│           │   ├── StatusActions.tsx  # Botões de transição válidos
│           │   ├── AIAnalysis.tsx     # Botão + display resultado análise
│           │   └── FilterBar.tsx      # Filtros + contadores
│           ├── hooks/
│           │   ├── useOrders.ts       # TanStack Query (listagem)
│           │   └── useOrderDetail.ts  # TanStack Query (detalhe)
│           └── services/
│               └── ordersApi.ts       # Chamadas HTTP ao orders-service
└── docs/
    └── adr/
        ├── 001-fastapi-choice.md
        ├── 002-redis-dual-purpose.md
        ├── 003-module-federation-strategy.md
        └── 004-postgresql-single-instance.md
```

---

## Comandos Úteis

### Desenvolvimento

```bash
# Subir stack completa
docker compose up

# Subir só os backends (sem frontend)
docker compose up postgres redis auth-service orders-service

# Ver logs de um serviço específico
docker compose logs -f orders-service

# Reconstruir um serviço após mudanças
docker compose up --build auth-service

# Executar testes (auth)
docker compose run --rm auth-service pytest tests/ -v

# Executar testes (orders)
docker compose run --rm orders-service pytest tests/ -v
```

### Banco de Dados

```bash
# Criar nova migration (auth)
docker compose run --rm auth-service alembic revision --autogenerate -m "description"

# Aplicar migrations
docker compose run --rm auth-service alembic upgrade head

# Conectar ao PostgreSQL
docker compose exec postgres psql -U pedidos -d auth_db
```

### Verificação de Qualidade

```bash
# Lint Python (auth)
docker compose run --rm auth-service ruff check app/

# Type check Python (auth)
docker compose run --rm auth-service mypy app/

# Type check TypeScript (shell)
docker compose run --rm shell tsc --noEmit

# Lint TypeScript (shell)
docker compose run --rm shell eslint src/
```

---

## Variáveis de Ambiente

### Obrigatórias

| Variável | Serviço | Descrição |
|----------|---------|-----------|
| `JWT_SECRET` | auth + orders | Chave para assinar/verificar JWTs (min 32 chars) |
| `POSTGRES_USER` | postgres | Usuário do banco de dados |
| `POSTGRES_PASSWORD` | postgres | Senha do banco de dados |

### Opcionais

| Variável | Serviço | Default | Descrição |
|----------|---------|---------|-----------|
| `ANTHROPIC_API_KEY` | orders | `` | Chave API Claude (fallback se ausente) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | auth | `1440` | Validade do JWT (24h) |
| `REDIS_CACHE_TTL` | orders | `300` | TTL do cache Redis em segundos |
| `LOG_LEVEL` | auth + orders | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`) |
| `ENV` | auth + orders | `development` | Ambiente (`development`, `production`) |

---

## Health Checks

```bash
# Auth service
curl http://localhost:8001/health

# Orders service
curl http://localhost:8002/health
```

Resposta esperada:
```json
{"status": "healthy", "service": "...", "database": "connected"}
```

---

## Fluxo Básico de Demonstração

1. Acessar http://localhost:3000
2. Registrar conta ou usar credenciais de seed
3. Navegar para "Pedidos" → visualizar lista com dados de seed
4. Criar novo pedido com múltiplos itens → verificar cálculo automático do total
5. Acessar detalhe → atualizar status → verificar transições válidas
6. Clicar "Analisar com IA" → aguardar resultado
7. Explorar filtros por status e prioridade
