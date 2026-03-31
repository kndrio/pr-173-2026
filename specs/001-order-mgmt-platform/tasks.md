# Tasks: Order Management Platform MVP

**Branch**: `001-order-mgmt-platform` | **Date**: 2026-03-30
**Input**: Design documents from `specs/001-order-mgmt-platform/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**Organization**: Tasks agrupadas em 6 fases incrementais, cada fase produzindo um incremento entregável e testável. Marcadores [USn] rastreiam cada tarefa à sua user story de origem.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependências entre si)
- **[Story]**: User story de origem (US1–US6, mapeadas da spec.md)
- **~Xh**: Estimativa de tempo de implementação

---

## Phase 1: Fundação — Monorepo + Auth Service

**Objetivo**: Stack base funcional com auth completo. Marco: `docker compose up auth-service postgres redis` sobe tudo com saúde.

**Independent Test**:
```bash
docker compose up -d postgres redis auth-service
curl http://localhost:8001/health
# → {"status":"healthy","service":"auth-service","database":"connected"}
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Teste","email":"t@t.com","password":"senha123"}'
# → 201 com id do usuário
curl -X POST http://localhost:8001/api/v1/auth/login \
  -d '{"email":"t@t.com","password":"senha123"}'
# → 200 com access_token
```

### Setup do Monorepo

- [x] T001 Criar estrutura de diretórios do monorepo conforme plan.md: `services/auth-service/`, `services/orders-service/`, `frontend/shell/`, `frontend/orders-mfe/`, `docs/adr/` ~0.5h
  - **Critério**: Todas as pastas existem; `.gitignore` configurado ignorando `.env`, `__pycache__`, `node_modules`, `dist/`

- [x] T001a [P] Criar `services/auth-service/pyproject.toml` e `services/orders-service/pyproject.toml` com seções `[tool.ruff]` (rules: E, W, F, I; target-version: py311) e `[tool.mypy]` (strict = true, ignore_missing_imports = true) ~0.5h
  - **Critério**: `ruff check app/` e `mypy app/` executam com as regras configuradas (não defaults); CI T081/T082 dependem deste arquivo existir

- [x] T001b [P] Criar `frontend/shell/eslint.config.js` e `frontend/orders-mfe/eslint.config.js` com regras: `@typescript-eslint/recommended`, `@typescript-eslint/no-explicit-any: error`, `react-hooks/rules-of-hooks: error` ~0.5h
  - **Critério**: `eslint src/` em cada MFE executa com as regras definidas; CI T083 depende deste arquivo existir

- [x] T002 [P] Criar `.env.example` na raiz com todas as variáveis documentadas: `JWT_SECRET`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `ANTHROPIC_API_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REDIS_URL` ~0.5h
  - **Critério**: Arquivo contém todas as variáveis com valores de exemplo; comentários explicativos; nenhum secret real no arquivo

- [x] T003 [P] Criar `docker-compose.yml` na raiz com serviços: `postgres` (PostgreSQL 16, 2 databases via init script), `redis` (Redis 7), `auth-service` (build local), com health checks e depends_on ~1h
  - **Critério**: `docker compose up postgres redis` sobe ambos; `docker compose ps` mostra status healthy; init script cria `auth_db` e `orders_db`

### Auth Service — Foundation

- [x] T004 [US1] Criar `services/auth-service/requirements.txt` com dependências: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic[email]`, `pydantic-settings`, `python-jose[cryptography]`, `passlib[bcrypt]`, `structlog` ~0.5h
  - **Critério**: `pip install -r requirements.txt` completa sem erros

- [x] T005 [US1] Criar `services/auth-service/app/core/config.py` com Settings (pydantic-settings): `JWT_SECRET`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES=1440`, `ENV`, `LOG_LEVEL` ~0.5h
  - **Critério**: `Settings()` carrega valores do `.env`; erro explícito se `JWT_SECRET` ausente

- [x] T006 [US1] Criar `services/auth-service/app/core/database.py` com `create_async_engine`, `async_session_factory`, `Base`, e dependency `get_db()` ~0.5h
  - **Critério**: `get_db()` retorna `AsyncSession`; `expire_on_commit=False`

- [x] T007 [US1] Criar `services/auth-service/app/core/security.py` com: `hash_password(plain)`, `verify_password(plain, hashed)`, `create_access_token(data)`, `decode_token(token)` ~1h
  - **Critério**: `hash_password("abc")` retorna hash bcrypt; `verify_password("abc", hash)` retorna True; `decode_token(create_access_token({"sub":"x"}))["sub"] == "x"`

- [x] T008 [US1] Criar `services/auth-service/app/models/user.py` com modelo SQLAlchemy `User`: campos `id` (UUID), `full_name`, `email` (unique), `hashed_password`, `role` (Enum), `is_active`, `created_at`, `updated_at` ~0.5h
  - **Critério**: `alembic revision --autogenerate` detecta o modelo; migration cria tabela `users` com índice em `email`

- [x] T009 [US1] Criar `services/auth-service/alembic/` configurado para `asyncpg`; criar primeira migration `001_create_users_table.py` ~0.5h
  - **Critério**: `alembic upgrade head` cria tabela `users` no `auth_db` sem erros

- [x] T010 [US1] Criar `services/auth-service/app/schemas/user.py` com: `UserCreate`, `UserLogin`, `UserResponse`, `TokenResponse`, `UserListResponse` (com paginação) ~0.5h
  - **Critério**: `UserCreate(full_name="x", email="x@x.com", password="12345678")` valida; `UserCreate(password="123")` lança ValidationError

- [x] T011 [US1] Criar `services/auth-service/app/api/v1/endpoints/auth.py` com `POST /register` (cria usuário, retorna UserResponse 201) e `POST /login` (valida credenciais, retorna TokenResponse 200) ~1.5h
  - **Critério**: Register com email duplicado → 409; senha curta → 422; login com senha errada → 401

- [x] T012 [US1] Criar `services/auth-service/app/dependencies.py` com `get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db))` que decodifica JWT e retorna User ~0.5h
  - **Critério**: Token inválido → 401; token expirado → 401; token válido → User object

- [x] T013 [US1] Criar `services/auth-service/app/api/v1/endpoints/users.py` com `GET /me` (retorna usuário autenticado) e `GET /users` (lista usuários ativos com paginação) ~0.5h
  - **Critério**: `/me` sem token → 401; `/me` com token válido → UserResponse; `/users` retorna lista com `total`, `page`, `pages`

- [x] T013a [US1] Criar `services/auth-service/app/core/logging.py` configurando structlog: `JSONRenderer` quando `ENV=production`, `ConsoleRenderer` quando `ENV=development`; função `configure_logging()` com campos obrigatórios `service="auth-service"`, `level`, `timestamp` ~0.5h
  - **Critério**: `configure_logging()` chamado no startup do app; `structlog.get_logger().info("test")` emite JSON válido em ENV=production; Constitution VII satisfeita desde Phase 1

- [x] T014 [US1] Criar `services/auth-service/app/main.py` com FastAPI app, CORS (origem `http://localhost:3000`), middleware `X-Request-ID` (gera UUID4 se ausente, injeta em structlog context), `GET /health` retornando status do banco, roteamento de endpoints, chamada a `configure_logging()` no startup ~1h
  - **Critério**: `/health` retorna 200 com `{"status":"healthy","database":"connected"}`; todo log de request inclui `request_id`; CORS aceita origem do shell

- [x] T015 [US1] Criar `services/auth-service/Dockerfile` multi-stage: stage `builder` (instala deps) + stage `runtime` (`python:3.11-slim`, usuário `appuser` non-root, copia só o necessário) ~1h
  - **Critério**: `docker build` completa sem erros; container roda como non-root (`docker exec ... whoami` ≠ `root`); tamanho final < 200MB

- [x] T016 [US1] Adicionar `auth-service` ao `docker-compose.yml` com build, env vars, port mapping `8001:8001`, depends_on postgres com condition `service_healthy` ~0.5h
  - **Critério**: `docker compose up auth-service` sobe com health check passando; migrations rodam no startup via `command: ["sh","-c","alembic upgrade head && uvicorn..."]`

- [x] T016a [US1] Criar `services/auth-service/tests/conftest.py` com fixtures básicas (async test client, DB de teste) e 3 testes mínimos em `tests/test_auth_smoke.py`: registro com sucesso, login com sucesso, login com senha errada (401) ~1h
  - **Critério**: `pytest tests/test_auth_smoke.py -v` passa com 3 testes ✅; Constitution V satisfeita para Phase 1 — comportamentos de Phase 1 têm cobertura mínima antes de merge

**Checkpoint Phase 1** ✅: Auth completo — registro, login, /me, listagem de usuários, health check, logging estruturado, testes mínimos. `docker compose up auth-service postgres redis` funciona.

---

## Phase 2: Orders Service — CRUD + Cache + Events

**Objetivo**: Orders Service completo com todos os endpoints, cache Redis e eventos Pub/Sub. Marco: fluxo completo de pedidos via curl.

**Independent Test**:
```bash
docker compose up -d postgres redis auth-service orders-service
# 1. Obter token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -d '{"email":"admin@pedidos.dev","password":"admin123!"}' | jq -r .access_token)
# 2. Criar pedido
curl -X POST http://localhost:8002/api/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"customer_name":"João","customer_email":"j@j.com","description":"Teste","items":[{"name":"Item","quantity":2,"unit_price":100}],"priority":"alta"}'
# → 201 com total_amount: 200.00
# 3. Listar
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/api/v1/orders
# → lista com 1 pedido
```

### Orders Service — Foundation

- [x] T017 [US2] Criar `services/orders-service/requirements.txt`: mesmas dependências base + `redis[hiredis]`, `httpx` ~0.25h
  - **Critério**: `pip install -r requirements.txt` completa sem erros

- [x] T018 [US2] Criar `services/orders-service/app/core/config.py` com Settings: `JWT_SECRET`, `DATABASE_URL` (orders_db), `REDIS_URL`, `ANTHROPIC_API_KEY` (opcional), `REDIS_CACHE_TTL=300` ~0.5h
  - **Critério**: Settings carrega corretamente; `ANTHROPIC_API_KEY` é `Optional[str] = None`

- [x] T019 [US2] [P] Criar `services/orders-service/app/core/database.py` (async engine, session factory para `orders_db`) ~0.25h
  - **Critério**: Conexão ao `orders_db` funciona; sessão isolada do `auth_db`

- [x] T020 [US2] [P] Criar `services/orders-service/app/core/redis.py` com factory `get_redis()` retornando cliente async Redis configurado com `REDIS_URL` ~0.5h
  - **Critério**: `get_redis()` conecta ao Redis; `await redis.ping()` retorna True

### Orders — Modelos e Migração

- [x] T021 [US2] Criar `services/orders-service/app/models/order.py` com modelos SQLAlchemy `Order` e `OrderItem` conforme data-model.md; enum `Priority` e `OrderStatus`; relationship `Order.items` com cascade delete ~1h
  - **Critério**: `alembic revision --autogenerate` detecta `orders` e `order_items`; índices em `status`, `priority`, `created_at`

- [x] T022 [US2] Criar `services/orders-service/alembic/` e primeira migration `001_create_orders_tables.py` ~0.5h
  - **Critério**: `alembic upgrade head` cria tabelas no `orders_db`; FK `order_items.order_id → orders.id` com ON DELETE CASCADE

### Orders — Schemas e Serviços

- [x] T023 [US2] Criar `services/orders-service/app/schemas/order.py` com: `OrderItemCreate`, `OrderCreate`, `OrderItemResponse`, `OrderResponse` (com itens), `OrderListItemResponse` (sem itens), `OrderListResponse` (paginada com `filters`), `OrderStatusUpdate`, `AIAnalysisResponse` ~1h
  - **Critério**: `OrderCreate` com `items=[]` lança ValidationError; `OrderItemCreate(quantity=0)` lança ValidationError

- [x] T024 [US2] Criar `services/orders-service/services/order_service.py` com funções async: `create_order(db, data, user_id)` calculando `total_amount` e `subtotal` de cada item, `get_order(db, order_id)`, `list_orders(db, filters, pagination)` ~2h
  - **Critério**: `create_order` com 2 itens retorna pedido com `total_amount` correto (soma dos subtotais); pedido criado com `status=pendente`

- [x] T025 [US3] Criar `services/orders-service/services/order_service.py` → adicionar função `update_order_status(db, order_id, new_status)` com validação de transições conforme state machine em data-model.md ~1h
  - **Critério**: `pendente → em_andamento` aceito; `concluido → em_andamento` lança ValueError com mensagem descritiva; `pendente → cancelado` aceito

### Orders — Cache e Eventos

- [x] T026 [US4] [P] Criar `services/orders-service/services/cache_service.py` com: `get_orders_cache(redis, key)`, `set_orders_cache(redis, key, data, ttl)`, `invalidate_orders_cache(redis)` usando SCAN + DEL com padrão `orders:list:*` ~1h
  - **Critério**: `set_orders_cache` persiste; `get_orders_cache` retorna dado; `invalidate_orders_cache` deleta todas as keys `orders:list:*` sem usar `KEYS *`

- [x] T027 [US2] [P] Criar `services/orders-service/services/event_service.py` com `publish_order_event(redis, event_type, order_id, extra_data)` publicando JSON no canal `orders` ~0.5h
  - **Critério**: `publish_order_event(redis, "order_created", uuid, {...})` publica mensagem JSON válida; testável com `redis-cli SUBSCRIBE orders`

### Orders — Endpoints

- [x] T028 [US2] Criar `services/orders-service/app/dependencies.py` com `get_current_user` que valida JWT usando `JWT_SECRET` compartilhado (sem chamada HTTP ao auth-service) ~0.5h
  - **Critério**: Token do auth-service é aceito pelo orders-service; token adulterado → 401

- [x] T029 [US2] Criar `services/orders-service/app/api/v1/endpoints/orders.py` com `POST /orders` (cria pedido, invalida cache, publica evento `order_created`) ~1h
  - **Critério**: POST com itens → 201 com `total_amount` calculado; POST sem itens → 422; evento publicado no Redis

- [x] T030 [US4] Criar endpoint `GET /orders` com paginação (`page`, `page_size`), filtros (`status`, `priority`), ordenação; servido do cache Redis se disponível; retorna `filters` com contadores de status e prioridade ~1.5h
  - **Critério**: Filtro `?status=pendente` retorna só pendentes; paginação `?page=2&page_size=5` retorna página correta; segunda chamada idêntica vem do cache (verificar via log)

- [x] T031 [US4] Criar endpoint `GET /orders/{order_id}` com dados completos incluindo itens; busca no DB (sem cache) ~0.5h
  - **Critério**: ID existente → 200 com `items` array; ID inexistente → 404; pedido de outro usuário → acessível (não há isolamento por usuário no MVP)

- [x] T032 [US3] Criar endpoint `PATCH /orders/{order_id}/status` com validação de transição, invalidação de cache e publicação de evento `order_updated` ~1h
  - **Critério**: Transição válida → 200; transição inválida → 422 com mensagem "Invalid status transition: X → Y"; cache invalidado após update

### Orders — Main e Docker

- [x] T032a [US2] Criar `services/orders-service/app/core/logging.py` (mesmo padrão do auth-service; campo `service="orders-service"`; propaga `request_id` recebido via header `X-Request-ID`) ~0.25h
  - **Critério**: Logging estruturado configurado antes de T033 (main.py); Constitution VII satisfeita desde Phase 2

- [x] T033 [US2] Criar `services/orders-service/app/main.py` com FastAPI app, CORS (origem `http://localhost:3000`), middleware `X-Request-ID`, `GET /health` verificando DB e Redis, router, chamada a `configure_logging()` ~0.5h
  - **Critério**: `/health` retorna `{"status":"healthy","database":"connected","redis":"connected"}`; logs incluem `request_id` e `service="orders-service"`

- [x] T034 [US2] Criar `services/orders-service/Dockerfile` multi-stage (python:3.11-slim, non-root) ~0.5h
  - **Critério**: `docker build` OK; non-root; tamanho < 200MB

- [x] T035 [US2] Adicionar `orders-service` ao `docker-compose.yml` com port `8002:8002`, depends_on postgres e redis healthy ~0.5h
  - **Critério**: `docker compose up orders-service` sobe; `curl http://localhost:8002/health` → 200

- [x] T035a [US2] Criar `services/orders-service/tests/conftest.py` com fixtures (async test client, DB de teste, Redis mockado) e 3 testes mínimos em `tests/test_orders_smoke.py`: criar pedido com total correto, listar pedidos, transição de status válida ~1h
  - **Critério**: `pytest tests/test_orders_smoke.py -v` passa com 3 testes ✅; Constitution V satisfeita para Phase 2

**Checkpoint Phase 2** ✅: Backend completo, logging estruturado ativo, testes mínimos passando. Todos os endpoints funcionam via curl. Redis caching e eventos ativos. ✅ IMPLEMENTADO

---

## Phase 3: Frontend — Shell MFE + Orders MFE

**Objetivo**: Interface funcional completa com login, listagem e criação de pedidos. Marco: fluxo completo no browser em `http://localhost:3000`.

**Independent Test**:
```
1. Abrir http://localhost:3000
2. Login com operador@pedidos.dev / operador123!
3. Ver listagem de pedidos (com dados de seed)
4. Criar pedido com 2 itens → ver total calculado
5. Acessar detalhe → atualizar status
```

### Shell MFE — Setup

- [ ] T036 [US1] Criar `frontend/shell/package.json` com dependências: `react`, `react-dom`, `react-router-dom`, `zustand`, `axios`, `react-hook-form`, `zod`, `@hookform/resolvers` + devDeps: `typescript`, `vite`, `@vitejs/plugin-react`, `@originjs/vite-plugin-federation`, `eslint`, `@types/react` ~0.5h
  - **Critério**: `npm install` completa sem erros; `npm run build` compila

- [ ] T037 [US1] Criar `frontend/shell/tsconfig.json` com `strict: true`, `target: "ESNext"`, `module: "ESNext"`, `moduleResolution: "bundler"` ~0.25h
  - **Critério**: `tsc --noEmit` passa sem erros em projeto vazio

- [ ] T038 [US1] Criar `frontend/shell/vite.config.ts` com `@originjs/vite-plugin-federation` como host, consumindo remote `ordersMfe` da URL `http://localhost:3001/assets/remoteEntry.js` ~1h
  - **Critério**: Build de produção inclui Module Federation; fallback documentado em ADR-003 se instável

### Shell MFE — Auth Store e Serviços

- [ ] T039 [US1] Criar `frontend/shell/src/store/authStore.ts` com Zustand store: estado `{ token: string|null, user: User|null }`, actions `login(token, user)` e `logout()` — token em memória (sem localStorage) ~0.5h
  - **Critério**: `useAuthStore.getState().login(token, user)` persiste em memória; após `logout()` estado volta a null; token NÃO está no localStorage (verificar via DevTools)

- [ ] T040 [US1] Criar `frontend/shell/src/services/authApi.ts` com funções: `registerUser(data)`, `loginUser(credentials)`, `getMe(token)` chamando `/api/auth/...` via axios ~0.5h
  - **Critério**: `loginUser({email,password})` retorna `{access_token, token_type}`; token injetado via axios interceptor em `Authorization: Bearer`

### Shell MFE — Páginas e Layout

- [ ] T041 [US1] Criar `frontend/shell/src/pages/LoginPage.tsx` com React Hook Form + Zod (`loginSchema`): campos email e senha, botão submit, loading state, mensagem de erro ~1h
  - **Critério**: Submit com campos vazios mostra erros de validação inline; submit válido chama `loginUser`, salva token no store, redireciona para `/`; credenciais erradas mostra "Email ou senha inválidos"

- [ ] T042 [US1] Criar `frontend/shell/src/pages/RegisterPage.tsx` com React Hook Form + Zod: campos nome, email, senha; link para login ~0.5h
  - **Critério**: Email duplicado → exibe erro do servidor; senha < 8 chars → erro Zod inline; sucesso → redireciona para `/`

- [ ] T043 [US1] Criar `frontend/shell/src/components/Layout.tsx` com header (logo + nome usuário + botão logout), sidebar (link "Pedidos"), área de conteúdo (`<Outlet />`) ~1h
  - **Critério**: Header exibe nome do usuário logado; logout limpa store e redireciona para `/login`; sidebar destaca link da rota ativa

- [ ] T044 [US1] Criar `frontend/shell/src/App.tsx` com React Router: rota `/login`, `/register` (públicas); rota `/` e `/pedidos/*` protegidas via `ProtectedRoute` (redireciona para `/login` se sem token); carrega `OrdersMfe` via lazy import do remote ~1h
  - **Critério**: Acesso a `/` sem token → redirect `/login`; após login → acesso às rotas protegidas; MFE carregado dinamicamente

### Shell MFE — Docker

- [ ] T045 [US1] Criar `frontend/shell/nginx.conf` com: serve `/` → `index.html` (SPA fallback), proxy `/api/auth/` → `http://auth-service:8001/`, proxy `/api/orders/` → `http://orders-service:8002/` ~0.5h
  - **Critério**: `nginx -t` passa; proxy das APIs funciona sem CORS issues; SPA routing funciona com reload da página

- [ ] T046 [US1] Criar `frontend/shell/Dockerfile` multi-stage: `node:20-alpine` builder (`npm ci && npm run build`) → `nginx:alpine` runtime (copia `dist/` e `nginx.conf`), non-root ~1h
  - **Critério**: `docker build` OK; imagem serve a SPA na porta 3000

- [ ] T047 [US1] Adicionar `shell` ao `docker-compose.yml` com port `3000:80`, depends_on auth-service e orders-service ~0.25h
  - **Critério**: `docker compose up shell` sobe; `curl http://localhost:3000` retorna HTML

### Orders MFE — Setup e Configuração

- [ ] T048 [US2] Criar `frontend/orders-mfe/package.json` com dependências: react, react-router-dom, `@tanstack/react-query`, `react-hook-form`, `zod`, `@hookform/resolvers`, axios + devDeps ~0.5h
  - **Critério**: `npm install && npm run build` OK

- [ ] T049 [US2] Criar `frontend/orders-mfe/vite.config.ts` como Module Federation remote, expondo `./OrdersApp` na porta 3001 ~0.5h
  - **Critério**: Build gera `remoteEntry.js`; shell consegue consumir o remote

- [ ] T050 [US2] Criar `frontend/orders-mfe/src/types/order.ts` com interfaces TypeScript: `Order`, `OrderItem`, `OrderListResponse`, `Priority`, `OrderStatus`, `CreateOrderDto`, `OrderFilters` ~0.5h
  - **Critério**: `tsc --noEmit` passa; sem uso de `any`

- [ ] T051 [US2] Criar `frontend/orders-mfe/src/services/ordersApi.ts` com funções axios: `fetchOrders(filters, pagination)`, `fetchOrder(id)`, `createOrder(data)`, `updateOrderStatus(id, status)`, `analyzeOrder(id)` — lê token do authStore do Shell ~1h
  - **Critério**: `fetchOrders()` chama `/api/orders`; `createOrder` chama POST; token incluído em todas as chamadas

- [ ] T052 [US4] [P] Criar hooks TanStack Query: `frontend/orders-mfe/src/hooks/useOrders.ts` (useQuery com filtros e paginação) e `useOrderDetail.ts` (useQuery por ID) ~0.5h
  - **Critério**: `useOrders({status:'pendente'})` retorna dados filtrados; refetch automático após mutação

- [ ] T053 [US2] [P] Criar hooks de mutação: `frontend/orders-mfe/src/hooks/useCreateOrder.ts` (useMutation + invalidate query) e `useUpdateStatus.ts` (useMutation + invalidate) ~0.5h
  - **Critério**: Após `createOrder` bem-sucedido, lista de pedidos é automaticamente refetchada

### Orders MFE — Componentes de Listagem

- [ ] T054 [US4] Criar `frontend/orders-mfe/src/components/StatusBadge.tsx` com badge colorido por status: pendente=amarelo, em_andamento=azul, concluido=verde, cancelado=cinza ~0.5h
  - **Critério**: Cada status renderiza badge com cor e texto corretos; visível em mobile e desktop

- [ ] T055 [US4] Criar `frontend/orders-mfe/src/components/FilterBar.tsx` com selects de status e prioridade; exibe contadores de cada categoria abaixo dos selects; botão "Limpar filtros" ~1h
  - **Critério**: Select de status altera `?status=` na query; contadores refletem dados da API (`filters.status_counts`); "Limpar filtros" reseta para sem filtro

- [ ] T056 [US4] Criar `frontend/orders-mfe/src/components/OrderList.tsx` com tabela responsiva (desktop) / cards (mobile) exibindo: cliente, descrição truncada, prioridade, `StatusBadge`, total, data; empty state quando sem resultados; loading skeleton ~1.5h
  - **Critério**: Tabela exibe dados corretamente; skeleton visível durante loading; "Nenhum pedido encontrado" quando lista vazia; clicar em linha navega para detalhe

- [ ] T057 [US4] Criar `frontend/orders-mfe/src/components/Pagination.tsx` com botões prev/next, indicador "Página X de Y" ~0.5h
  - **Critério**: Última página desabilita botão "próxima"; primeira página desabilita "anterior"; mudança de página refetch os dados

### Orders MFE — Formulário de Criação

- [ ] T058 [US2] Criar `frontend/orders-mfe/src/components/OrderForm.tsx` com React Hook Form + Zod (`orderCreateSchema`): campos cliente, email, descrição, prioridade, observações; seção de itens com `useFieldArray` para adição/remoção dinâmica; total calculado em tempo real ~2h
  - **Critério**: Botão "Adicionar item" insere nova linha com campos nome/quantidade/preço; botão "Remover" remove linha; total atualiza sem submit; submit sem itens → erro Zod; submit válido → POST e redirect para lista

### Orders MFE — Detalhe e Status

- [ ] T059 [US3] Criar `frontend/orders-mfe/src/components/StatusActions.tsx` recebendo `currentStatus` e exibindo apenas botões de transição válidos: `pendente` → [Iniciar, Cancelar]; `em_andamento` → [Concluir, Cancelar]; outros → nenhum botão; loading state durante PATCH ~1h
  - **Critério**: Pedido `pendente` mostra "Iniciar Atendimento" e "Cancelar"; pedido `concluido` mostra nenhum botão; click em botão chama `updateOrderStatus`, mostra spinner, atualiza badge após sucesso

- [ ] T060 [US3] [P] Criar `frontend/orders-mfe/src/components/OrderDetail.tsx` com: dados completos do pedido, tabela de itens com subtotais, total destacado, `StatusBadge`, `StatusActions`, seção de análise IA ~1.5h
  - **Critério**: Todos os campos exibidos; tabela de itens com subtotal por linha; loading skeleton durante fetch; 404 → mensagem "Pedido não encontrado"

### Orders MFE — App e Docker

- [ ] T061 [US2] Criar `frontend/orders-mfe/src/App.tsx` com rotas: `/` → OrderList, `/novo` → OrderForm, `/:id` → OrderDetail; wrapeado em `QueryClientProvider` ~0.5h
  - **Critério**: Navegação entre rotas funciona; QueryClient configurado com `staleTime: 30_000`

- [ ] T062 [US2] Criar `frontend/orders-mfe/Dockerfile` multi-stage (node:20-alpine → nginx:alpine, non-root), porta 3001 ~0.5h
  - **Critério**: `docker build` OK; `remoteEntry.js` acessível em `http://localhost:3001/assets/remoteEntry.js`

- [ ] T063 [US2] Adicionar `orders-mfe` ao `docker-compose.yml`, porta `3001:80` ~0.25h
  - **Critério**: `docker compose up orders-mfe` sobe; shell carrega o MFE remote corretamente

**Checkpoint Phase 3** ✅: Fluxo completo no browser: login → listar pedidos → criar pedido → ver detalhe → atualizar status.

---

## Phase 4: Integração + Estabilização

**Objetivo**: Stack completa funcionando end-to-end com dados realistas. Marco: **versão entregável** que pode ser demonstrada.

**Independent Test**:
```
Fluxo completo: login → criar pedido com 3 itens → listar → filtrar por status
→ acessar detalhe → atualizar status para em_andamento → verificar cache invalidado
→ tentar atualização inválida (concluido → pendente) → ver mensagem de erro
```

- [ ] T064 Criar script de seed `services/orders-service/app/core/seed.py` com 3 usuários (admin, gestor, operador) no auth_db e 15 pedidos variados (diferentes status, prioridades, múltiplos itens) no orders_db ~2h
  - **Critério**: `python seed.py` popula os bancos; usuários têm credenciais conforme quickstart.md; pedidos cobrem todos os status e prioridades

- [ ] T065 Integrar seed no `docker-compose.yml` como serviço `seeder` com `depends_on` auth-service e orders-service, `restart: "no"` ~0.5h
  - **Critério**: `docker compose up` executa seed automaticamente na primeira inicialização; re-runs são idempotentes

- [ ] T066 Configurar interceptor axios global no frontend: adicionar header `Authorization: Bearer <token>` em todas as chamadas (lendo do authStore), e interceptor de resposta para 401 (limpar store + redirect para `/login`) ~0.5h
  - **Critério**: Token incluído automaticamente após login em todas as chamadas; sessão expirada redireciona para `/login` sem ação manual; CORS já está configurado desde T014/T033 (Phase 1/2)

- [ ] T067 Implementar error handling global no frontend: interceptor axios para 401 (redirect login), 422 (exibir erros de validação), 500 (mensagem genérica amigável); `ErrorBoundary` nos MFEs ~1h
  - **Critério**: Sessão expirada → redirect automático para `/login`; erro 422 do servidor → campos com erros destacados; erro 500 → toast/banner com mensagem amigável

- [ ] T068 [P] Implementar loading states consistentes: skeleton loaders na listagem, spinner em botões durante mutações, desabilitar botão submit durante envio ~0.5h
  - **Critério**: Nenhum elemento fica em estado "vazio" sem feedback visual; botão de criação desabilitado durante POST

- [ ] T069 [P] Implementar empty states: listagem sem pedidos, listagem com filtro sem resultados (com sugestão de limpar filtro), detalhe com ID inválido ~0.5h
  - **Critério**: Estados vazios têm ícone + mensagem descritiva + ação sugerida

- [ ] T070 Verificar fluxo Module Federation em produção (docker compose up completo); se instável, implementar fallback NGINX com shell servindo `/pedidos` diretamente do orders-mfe compilado ~1.5h
  - **Critério**: `http://localhost:3000/pedidos` funciona com reload direto; MFE renderiza sem erros de console

**Checkpoint Phase 4** ✅: Versão entregável. Demo completa possível do início ao fim.

---

## Phase 5: Qualidade + Bônus

**Objetivo**: Testes automatizados, CI, análise de IA e observabilidade completa.

### Testes Backend

- [ ] T071 [US1] Criar `services/auth-service/tests/conftest.py` com fixtures: async test client, DB em memória (SQLite async) ou PostgreSQL de teste, usuário de teste ~1h
  - **Critério**: `pytest tests/` roda sem erros; fixtures criam e limpam state entre testes

- [ ] T072 [US1] Criar `services/auth-service/tests/test_auth.py` com testes: registro sucesso, registro email duplicado, registro senha curta, login sucesso, login senha errada, login email inexistente ~1.5h
  - **Critério**: 6+ testes passando; cobertura dos cenários de erro documentados no contrato

- [ ] T073 [US1] Criar `services/auth-service/tests/test_users.py` com testes: `/me` com token válido, `/me` sem token, `/users` com paginação ~0.5h
  - **Critério**: 3+ testes passando

- [ ] T074 [US2] Criar `services/orders-service/tests/conftest.py` com fixtures: test client, DB teste, Redis mock ou Redis de teste, usuário autenticado (token válido) ~1h
  - **Critério**: `pytest tests/` roda; Redis mockado ou usando testcontainers

- [ ] T075 [US2] Criar `services/orders-service/tests/test_orders.py` com testes: criar pedido (cálculo total correto), criar sem itens (422), listar com filtros, buscar por ID, buscar ID inexistente (404) ~2h
  - **Critério**: 8+ testes passando; verificar que `total_amount == sum(qty*price)`

- [ ] T076 [US3] Adicionar testes em `test_orders.py`: transições válidas (pendente→em_andamento, em_andamento→concluido, qualquer→cancelado), transições inválidas (concluido→pendente → 422) ~1h
  - **Critério**: 4+ testes cobrindo a state machine; transição inválida retorna 422 com mensagem correta

### Análise IA (US5)

- [ ] T077 [US5] Criar `services/orders-service/services/ai_service.py` com `analyze_order(order: Order) → AIAnalysisResponse`: chama Anthropic API via httpx async com timeout 8s, prompt estruturado pedindo JSON `{suggested_priority, executive_summary}`; em caso de timeout/erro → fallback rule-based ~2h
  - **Critério**: Com `ANTHROPIC_API_KEY` válida → análise retorna sugestão da IA com `analysis_source: "ai"`; sem chave ou timeout → fallback retorna sugestão por regras com `analysis_source: "rules"`; nunca retorna 5xx

- [ ] T078 [US5] Criar endpoint `POST /api/v1/orders/{order_id}/analyze` que chama `ai_service.analyze_order` ~0.5h
  - **Critério**: Endpoint retorna 200 em ambos os casos (IA e fallback); 404 se pedido não existe

- [ ] T079 [US5] Criar `frontend/orders-mfe/src/components/AIAnalysis.tsx` com botão "Analisar com IA", loading spinner durante análise, exibição de `suggested_priority` (com badge) e `executive_summary` (parágrafo), indicador `analysis_source` ~1h
  - **Critério**: Botão desabilitado durante análise; resultado exibido após retorno; fallback não mostra mensagem de erro ao usuário; exibe "Análise por IA" ou "Análise automática" conforme `analysis_source`

- [ ] T080 [US5] Criar `services/orders-service/tests/test_ai_service.py` com mock da API Anthropic: teste com resposta válida, teste com timeout (verifica fallback), teste de rule-based logic ~1h
  - **Critério**: 3+ testes; fallback retorna prioridade correta para pedido com total > 10000

### CI e Observabilidade

- [ ] T081 [P] Criar `.github/workflows/auth-service.yml` com job: trigger em push `services/auth-service/**`, steps: checkout, setup Python 3.11, install deps, `ruff check`, `mypy app/`, `pytest tests/ -v` ~1h
  - **Critério**: Workflow executa em push; falha de teste bloqueia merge; jobs paralelos por serviço

- [ ] T082 [P] Criar `.github/workflows/orders-service.yml` (mesmo padrão, para orders-service) ~0.5h
  - **Critério**: CI independente do auth-service; roda em paralelo

- [ ] T083 [P] Criar `.github/workflows/frontend.yml` com jobs para shell e orders-mfe: `npm ci`, `tsc --noEmit`, `eslint src/`, `npm run build` ~1h
  - **Critério**: Type errors ou lint errors bloqueiam build

- [ ] T084 [P] Verificar e completar cobertura de logging: auditar todos os endpoints de ambos os serviços garantindo que operações críticas (criação de pedido, update de status, análise IA, falhas de auth) emitem logs estruturados com `request_id`; adicionar logs ausentes ~0.5h
  - **Critério**: `docker compose logs orders-service` em ENV=production exibe JSON válido para cada request; `request_id` rastreável de ponta a ponta entre auth e orders; logging.py já criado em T013a/T032a — esta task completa a cobertura

**Checkpoint Phase 5** ✅: Testes passando, CI configurado, análise IA funcionando, logs estruturados.

---

## Phase 6: Documentação + Polish

**Objetivo**: Projeto entregável com documentação completa e UI polida.

### Admin — Listagem de Usuários (US6)

- [ ] T085 [US6] Adicionar página de usuários no shell: `frontend/shell/src/pages/UsersPage.tsx` com tabela paginada de usuários (nome, email, papel) consumindo `GET /api/auth/users` ~1h
  - **Critério**: Link "Usuários" na sidebar navega para lista; tabela exibe usuários ativos com paginação

### Documentação

- [ ] T086 [P] Criar `docs/adr/001-fastapi-choice.md`: ADR documentando escolha do FastAPI vs Django vs Flask com contexto, decisão, consequências ~0.5h
  - **Critério**: ADR segue formato padrão (Context, Decision, Consequences); referenciado no README

- [ ] T087 [P] Criar `docs/adr/002-redis-dual-purpose.md`: ADR documentando uso do Redis para cache + Pub/Sub (dual-purpose) ~0.25h
  - **Critério**: ADR documenta tradeoff e alternativa rejeitada (2 serviços separados)

- [ ] T088 [P] Criar `docs/adr/003-module-federation-strategy.md`: ADR documentando MFE com Module Federation como primário e fallback NGINX ~0.25h
  - **Critério**: ADR documenta risco e plano de contingência

- [ ] T089 [P] Criar `docs/adr/004-postgresql-single-instance.md`: ADR documentando 1 container PostgreSQL com 2 databases lógicos ~0.25h
  - **Critério**: ADR documenta tradeoff MVP vs produção

- [ ] T090 Criar `README.md` completo na raiz com: descrição do projeto, diagrama de arquitetura (Mermaid ou ASCII), stack tecnológica com justificativas, setup em 3 passos (clone → .env → docker compose up), credenciais de demo, estrutura do projeto, links para Swagger docs, nota sobre uso de IA (SpecKit + Claude) ~3h
  - **Critério**: Alguém sem contexto consegue subir o projeto em < 5 minutos seguindo o README; diagrama de arquitetura mostra todos os serviços e suas conexões

### UI Polish

- [ ] T091 [P] Implementar design responsivo: testar em 375px (mobile), 768px (tablet), 1280px (desktop); ajustar tabela de pedidos para exibir cards em mobile ~1h
  - **Critério**: Nenhum scroll horizontal em 375px; navegação acessível em touch; formulário de pedido utilizável em mobile

- [ ] T092 [P] Implementar feedback visual de sucesso: toasts/notificações após criar pedido, atualizar status, completar análise IA ~0.5h
  - **Critério**: Ação bem-sucedida mostra toast verde por 3s; erro mostra toast vermelho

- [ ] T093 Verificação final: `docker compose down -v && docker compose up --build`; executar checklist completo de quality gates da constituição; verificar `GET /health` em ambos os serviços; confirmar que seed data carregou; testar fluxo completo ~1h
  - **Critério**: Todos os quality gates da constituição passam (ruff, mypy, eslint, tsc, pytest, docker build, health checks, sem secrets); fluxo end-to-end funcional

**Checkpoint Phase 6** ✅: Projeto completo, documentado e polido. Pronto para entrega.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: Sem dependências — iniciar imediatamente
- **Phase 2**: Depende de Phase 1 completa (PostgreSQL, Redis, JWT secret estabelecidos)
- **Phase 3**: Depende de Phase 1 completa (auth API) e Phase 2 parcialmente (endpoints de pedidos)
  - Shell (T036–T047) pode começar após Phase 1
  - Orders MFE (T048–T063) requer Phase 2 completa
- **Phase 4**: Depende de Phase 3 completa
- **Phase 5**: Pode começar em paralelo com Phase 4 (testes independentes de seed)
- **Phase 6**: Depende de Phase 5 (para ADRs informados); UI polish pode rodar em paralelo

### User Story Dependencies

| User Story | Depende de | Pode começar após |
|------------|------------|-------------------|
| US1 — Auth | Nenhuma | T003 (postgres/redis up) |
| US2 — Criar pedido | US1 (JWT) | T016 (auth-service up) |
| US3 — Status | US2 (pedidos existem) | T035 (orders-service up) |
| US4 — Listar/filtrar | US2 (pedidos existem) | T035 |
| US5 — Análise IA | US2 (pedido criado) | T035 |
| US6 — Admin usuários | US1 (users endpoint) | T016 |

### Oportunidades de Paralelismo (maior impacto)

```
Após T003 (docker-compose base):
├── T004–T016 (auth-service) — um desenvolvedor
└── T017–T020 (orders foundation setup) — outro desenvolvedor

Após Phase 1 (T016 completo):
├── T036–T047 (Shell MFE)
└── T021–T035 (Orders Service backend)

Dentro de Phase 3, após T047 (shell up):
├── T052 (hooks TanStack Query) — paralelo
├── T053 (mutation hooks) — paralelo
├── T054 (StatusBadge) — paralelo
└── T055 (FilterBar) — paralelo

Phase 5 testes — todos marcados [P] podem rodar em paralelo:
├── T072 (test_auth.py)
├── T075 (test_orders.py)
├── T081 (CI auth)
├── T082 (CI orders)
└── T083 (CI frontend)
```

---

## Parallel Example: Phase 1 + Phase 3

```bash
# Após T003 (docker-compose base) — iniciar em paralelo:
Task "T036: shell/package.json com todas as dependências"
Task "T017: orders-service/requirements.txt"
Task "T018: orders-service/app/core/config.py"
Task "T019: orders-service/app/core/database.py"
Task "T020: orders-service/app/core/redis.py"
```

---

## Implementation Strategy

### MVP Mínimo (Phase 1 + 2 + 3 parcial)
1. Completar Phase 1 → auth backend funcional
2. Completar Phase 2 → orders backend funcional
3. Completar Shell + listagem básica (T036–T056) → UI navegável
4. **PARAR e VALIDAR**: fluxo via browser com dados de seed
5. Entregar se necessário

### Entrega Completa (Todas as Fases)
1. Phase 1 → Phase 2 → Phase 3 → Phase 4 (marco entregável)
2. Phase 5 (testes + CI + IA) → Phase 6 (docs + polish)
3. Verificação final → entrega

### Estratégia de Time (2 devs)
- **Dev A**: Backend (Phase 1 + 2 + testes Phase 5)
- **Dev B**: Frontend (Phase 3) — pode iniciar Shell após Phase 1
- Integração em Phase 4 (ambos)
- Phase 6 dividido por área

---

## Resumo

| Fase | Tarefas | Estimativa | Marco |
|------|---------|------------|-------|
| Phase 1 — Fundação | T001–T016a (20 tarefas) | ~15h | Auth completo + logging + testes mínimos |
| Phase 2 — Orders Backend | T017–T035a (22 tarefas) | ~16h | Backend completo + logging + testes mínimos |
| Phase 3 — Frontend | T036–T063 (28 tarefas) | ~22h | Fluxo completo no browser |
| Phase 4 — Integração | T064–T070 (7 tarefas) | ~6.5h | Versão entregável |
| Phase 5 — Qualidade | T071–T084 (14 tarefas) | ~12.5h | Testes completos + CI + IA |
| Phase 6 — Docs + Polish | T085–T093 (9 tarefas) | ~8h | Entrega final |
| **Total** | **100 tarefas** | **~80h** | — |

*+7 tarefas adicionadas pela remediação: T001a, T001b, T013a, T016a, T032a, T035a (novas) + T084 convertida de setup para verificação.*

---

## Notes

- `[P]` = arquivos diferentes, sem dependências mútuas — executar em paralelo para ganho de velocidade
- `[USn]` = rastreabilidade para a user story de origem na spec.md
- Estimativas em `~Xh` são para implementação direta; revisão/debugging pode adicionar 20-30%
- Commitar após cada task ou grupo lógico de tasks (`T001–T003`, `T004–T016`, etc.)
- Parar em qualquer Checkpoint para validar independentemente antes de avançar
- Se Module Federation instável (T070), fallback NGINX é aceitável e documentado — não bloqueia entrega
