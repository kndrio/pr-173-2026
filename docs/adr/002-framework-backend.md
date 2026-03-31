# ADR-002: FastAPI como Framework Backend

**Status**: Aceito  
**Data**: 2026-03-27  
**Autores**: Kennedy Carvalho

---

## Contexto

O desafio exige dois microserviços Python independentes com autenticação JWT,
PostgreSQL, testes automatizados e documentação de API. As opções relevantes no
ecossistema Python são Django (REST Framework), Flask e FastAPI.

O critério de decisão não é "qual framework é mais popular" mas "qual framework
entrega mais valor demonstrável com menos configuração em um contexto de PMV com
microserviços".

---

## Decisão

Adotar **FastAPI** para ambos os serviços (`auth-service` e `orders-service`).

**Alternativas avaliadas:**

| Critério | Django DRF | Flask | FastAPI |
|----------|-----------|-------|---------|
| Async nativo | Parcial (ASGI) | Não | Sim |
| Validação de dados | Serializers (verboso) | Manual | Pydantic v2 (nativo) |
| Documentação OpenAPI | Plugin adicional | Plugin adicional | Automática |
| Boilerplate inicial | Alto | Médio | Baixo |
| Type hints integrados | Não | Não | Sim |
| Adequação a microserviços | Baixa | Média | Alta |

**Por que não Django:**
Django é excelente para monolitos com painel administrativo, ORM opinativo e
autenticação embutida. Para microserviços que precisam ser leves e independentes,
o Django carrega overhead desnecessário (ORM síncrono por padrão, admin panel,
sistema de templates) sem adicionar valor.

**Por que não Flask:**
Flask é flexível mas requer integração manual de cada componente: validação,
serialização, documentação, async. O resultado seria um FastAPI menos eficiente.

---

## Consequências

### Positivas

- **Swagger automático**: `/docs` disponível sem configuração adicional — avaliadores
  podem testar a API diretamente no browser.
- **Pydantic v2**: validação e serialização com type hints Python nativos;
  `@computed_field` para `total_amount` calculado server-side.
- **Async end-to-end**: `async def` nos endpoints + `asyncpg` + SQLAlchemy async =
  I/O não-bloqueante em toda a stack de banco de dados.
- **Type safety**: mypy verifica toda a camada de request/response sem configuração
  adicional — os tipos Pydantic são os tipos Python.
- **Startup rápido**: imagem final ~150MB, startup em ~2s vs ~8s de Django.

### Negativas

- **Sem admin embutido**: gerenciamento de dados requer endpoints manuais ou
  ferramentas externas (pgAdmin, scripts). Aceitável para PMV sem requisito de admin.
- **Ecossistema menor**: menos plugins de terceiros comparado a Django. Para os
  requisitos deste projeto, o ecossistema core é suficiente.
- **Curva de learning em Pydantic v2**: quebras de compatibilidade com v1 requerem
  atenção (ex: `model_validator` vs `field_validator` para evitar mutation in-place).

### Decisão de escopo associada

Migrações via Alembic (não `alembic --autogenerate` em produção sem revisão),
SQLAlchemy 2.0 async com `AsyncSession`, e `asyncpg` como driver PostgreSQL.
