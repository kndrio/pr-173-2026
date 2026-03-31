# Research: Order Management Platform MVP

**Branch**: `001-order-mgmt-platform` | **Date**: 2026-03-30
**Phase**: 0 — Pre-design research and decision rationale

---

## 1. Module Federation com Vite — Estratégia e Estabilidade

**Decision**: `@originjs/vite-plugin-federation` como estratégia primária; fallback para NGINX reverse proxy com apps independentes.

**Rationale**:
- `@originjs/vite-plugin-federation` implementa Webpack Module Federation no ecossistema Vite. É a solução mais adotada para MFE com Vite em 2024-2025.
- Limitações conhecidas: requer `build.target: 'esnext'` e pode ter instabilidade em HMR durante desenvolvimento — em produção (bundles compilados) é estável.
- A estratégia de fallback (apps independentes + NGINX routing) garante entregabilidade mesmo se o Module Federation apresentar problemas durante o desenvolvimento.
- Para o MVP, o Shell expõe `AuthContext` e `Layout` como remotes; o Orders MFE consome esses remotes e expõe seus próprios componentes de CRUD.

**Alternatives Considered**:
- Webpack 5 Module Federation: descartado — não alinha com stack Vite escolhida.
- single-spa: descartado — overhead de framework adicional injustificado para 2 MFEs.
- iframes: descartado — má experiência de usuário e isolamento excessivo para contexto compartilhado de auth.

**Risco mitigado**: Build de produção validado via `docker compose build` no CI. Se falhar, NGINX routing com apps independentes entra como fallback documentado em ADR-003.

---

## 2. JWT — Shared Secret vs PKI entre Serviços

**Decision**: JWT com shared secret via variável de ambiente (`JWT_SECRET`), algoritmo HS256.

**Rationale**:
- Para 2 serviços no mesmo `docker-compose`, shared secret é pragmaticamente correto: simples, sem overhead de rotação de chaves PKI.
- O orders-service valida JWTs emitidos pelo auth-service usando o mesmo `JWT_SECRET` — sem chamada de rede entre serviços para validação (stateless).
- O segredo é injetado via env var (`.env` não versionado, `.env.example` documentado).
- Expiração padrão: 24 horas (configurável via `ACCESS_TOKEN_EXPIRE_MINUTES`).

**Alternatives Considered**:
- RS256 com PKI: justificado apenas para múltiplos domínios de confiança ou escala empresarial — overhead desnecessário para MVP.
- Validação via chamada HTTP ao auth-service: cria acoplamento síncrono e ponto único de falha — descartado.
- Refresh tokens: valor agregado após MVP, não bloqueante para o desafio.

---

## 3. Redis — Cache TTL e Estratégia de Invalidação

**Decision**: TTL de 5 minutos para listagens de pedidos; invalidação proativa (delete-on-write).

**Rationale**:
- Cache key pattern: `orders:list:{status}:{priority}:{page}:{page_size}` — granular o suficiente para invalidar apenas o que mudou.
- Invalidação on-write: ao criar ou atualizar um pedido, deletar todas as keys com padrão `orders:list:*` via `SCAN + DEL` (sem `KEYS *` em produção).
- TTL de 5 min como safety net: garante que o cache não serve dados excessivamente stale mesmo se a invalidação falhar.
- Redis Pub/Sub: canal `orders` com mensagens JSON `{event: "order_created"|"order_updated", order_id: ..., timestamp: ...}`.

**Alternatives Considered**:
- Cache-aside com TTL longo (1h): não adequado para dados operacionais que mudam frequentemente.
- Write-through cache: complexidade adicional sem benefício claro para listagens paginadas.
- Memcached: descartado — Redis já cobre cache + Pub/Sub com uma única dependência (pragmatismo).

---

## 4. Anthropic Claude API — Integração e Fallback

**Decision**: Integração via `httpx` assíncrono com `claude-sonnet-4-20250514`; fallback baseado em regras quando API indisponível.

**Rationale**:
- `httpx` async alinha com o modelo async do FastAPI — sem bibliotecas adicionais além do SDK Anthropic.
- Prompt estruturado: envia `description`, `items` (lista) e `priority` atual do pedido; espera resposta JSON com `suggested_priority` e `executive_summary`.
- Timeout de 8 segundos (dentro do SC-003 de 10s).
- Fallback rule-based: prioridade sugerida baseada em heurísticas de valor total + número de itens + palavras-chave na descrição (ex: "urgente", "crítico" → prioridade alta).

**Fallback Logic** (rule-based):
```
total_value = sum(item.quantity * item.unit_price)
IF "urgente" OR "crítico" OR "emergência" in description.lower(): priority = "urgente"
ELIF total_value > 10000 OR len(items) > 10: priority = "alta"
ELIF total_value > 1000 OR len(items) > 5: priority = "media"
ELSE: priority = "baixa"
summary = f"Pedido de {customer_name} com {len(items)} item(ns), total R$ {total_value:.2f}."
```

**Alternatives Considered**:
- SDK oficial Anthropic (`anthropic` package): alternativa válida; `httpx` direto evita uma dependência mas o SDK é aceitável.
- Streaming: não necessário para este caso de uso (resposta única, estruturada).

---

## 5. SQLAlchemy 2.0 Async — Gestão de Sessões

**Decision**: `AsyncSession` com `async_sessionmaker`; dependency injection via FastAPI `Depends`.

**Rationale**:
- `create_async_engine` com `postgresql+asyncpg` driver.
- Sessão por request via `AsyncSession` — garante isolamento de transação e cleanup automático via `try/finally` ou context manager.
- `expire_on_commit=False` para evitar lazy loading após commit em contexto async.

**Pattern**:
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

---

## 6. Estrutura de Monorepo — Decisão de Layout

**Decision**: Monorepo com `services/` para backend e `frontend/` para MFEs; `docker-compose.yml` na raiz.

**Rationale**:
- Facilita `docker-compose up` na raiz sem navegação entre diretórios.
- CI paralelo por serviço via `paths` filter no GitHub Actions.
- Cada serviço tem seu próprio `requirements.txt` e `Dockerfile` — deployável independentemente.
- Sem ferramentas de monorepo (Nx, Turborepo) — overhead desnecessário para 4 projetos.

---

## 7. Logging — structlog com Correlation ID

**Decision**: `structlog` com renderer JSON em produção; `X-Request-ID` propagado via middleware FastAPI.

**Rationale**:
- Middleware gera `request_id` (UUID4) se não presente no header; injeta no contexto structlog.
- Campos obrigatórios em todo log: `service`, `level`, `timestamp`, `request_id`, `method`, `path`.
- Em desenvolvimento: `ConsoleRenderer` colorido para legibilidade. Em produção (`ENV=production`): `JSONRenderer`.

---

## 8. Banco de Dados — Um Container, Dois Databases

**Decision**: PostgreSQL único com databases `auth_db` e `orders_db` — isolamento lógico.

**Rationale**:
- Dois containers PostgreSQL em docker-compose aumentam tempo de startup e uso de memória sem benefício para MVP.
- Isolamento lógico (databases separados) garante que auth-service e orders-service não compartilham tabelas.
- Em produção real, a migração para instâncias separadas seria transparente (mudança de `DATABASE_URL`).
- Cada serviço se conecta ao seu database via `DATABASE_URL` própria — sem acoplamento.

**Nota ADR**: Decisão documentada em ADR-004. Em staging/produção, databases separados são recomendados.

---

## Resoluções de NEEDS CLARIFICATION

Nenhum marcador `[NEEDS CLARIFICATION]` foi identificado na spec. Todos os aspectos técnicos foram decididos pelo engenheiro responsável no input do `/speckit.plan` e documentados acima.
