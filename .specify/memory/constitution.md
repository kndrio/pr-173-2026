<!--
SYNC IMPACT REPORT
==================
Version change: (template não versionado) → 1.0.0
Tipo de bump: MINOR — primeira constituição concreta, substituindo template em branco.

Princípios adicionados (10 novos, template tinha 5 placeholders):
  - I.   Arquitetura: Microserviços e Microfrontends
  - II.  Stack Backend: Python/FastAPI/PostgreSQL
  - III. Stack Frontend: React/TypeScript/Vite
  - IV.  Infraestrutura: Docker Compose + GitHub Actions
  - V.   Qualidade: Type Hints, Testes, Linting
  - VI.  Segurança: JWT, LGPD, Validação
  - VII. Observabilidade: Logs Estruturados + Correlation ID
  - VIII.Pragmatismo: PMV Funcional > Completude Teórica
  - IX.  Documentação: README como Artefato de Primeira Classe
  - X.   IA como Método: Spec-Driven Development

Seções adicionadas:
  - "Restrições e Padrões Técnicos" (substituiu [SECTION_2_NAME])
  - "Fluxo de Desenvolvimento e Quality Gates" (substituiu [SECTION_3_NAME])

Seções removidas:
  - Nenhuma (templates completamente substituídos)

Templates avaliados:
  ✅ .specify/memory/constitution.md — este arquivo (escrito agora)
  ⚠  .specify/templates/plan-template.md — "Constitution Check" é preenchido
     dinamicamente em cada plano; nenhuma edição necessária no template base.
  ⚠  .specify/templates/spec-template.md — estrutura genérica alinha com a
     constituição; path conventions de microserviços serão definidos em plan.md.
  ⚠  .specify/templates/tasks-template.md — "Web app" path convention é o mais
     próximo; layout multi-serviço deve ser explicitado em cada plan.md.
  ✅ .specify/templates/agent-file-template.md — template dinâmico, sem referências
     desatualizadas.

TODOs deferidos:
  - Nenhum. RATIFICATION_DATE definido como 2026-03-27 (data de primeira autoria).
-->

# Plataforma de Gestão de Pedidos — Constituição

## Princípios Fundamentais

### I. Arquitetura: Microserviços e Microfrontends

A arquitetura DEVE ser baseada em microserviços no backend e microfrontends no frontend.
O projeto DEVE ter no mínimo dois serviços backend e dois MFEs independentes.
Cada serviço backend DEVE ter seu próprio banco de dados — compartilhamento de banco entre
serviços é proibido. Cada serviço DEVE ser deployável e testável de forma independente.

**Rationale**: Isolamento de domínios garante escalabilidade independente e reduz acoplamento.
O desafio técnico exige explicitamente esta separação como demonstração de maturidade arquitetural.

### II. Stack Backend: Python/FastAPI/PostgreSQL

O backend DEVE ser implementado em Python (>= 3.11) com FastAPI (>= 0.100).
O banco de dados de cada serviço DEVE ser PostgreSQL (>= 15).
Dependências DEVEM ser gerenciadas com `pip` + `requirements.txt` ou `pyproject.toml`.
Migrações DEVEM usar Alembic. Alternativas de linguagem ou framework requerem ADR
justificando o desvio antes da implementação.

**Rationale**: FastAPI oferece async nativo, validação via Pydantic e geração automática
de Swagger/OpenAPI — escolha ideal para microserviços leves e demonstrável em desafio técnico.

### III. Stack Frontend: React/TypeScript/Vite

O frontend DEVE ser implementado em React com TypeScript (modo strict, >= 5.0) e
bundled com Vite. Cada MFE DEVE ser uma SPA independente. A composição de MFEs DEVE usar
Module Federation ou composição via reverse proxy. O uso de `any` em TypeScript é proibido
sem comentário inline justificando a exceção. Node.js DEVE ser >= 20 (LTS).

**Rationale**: React + TypeScript + Vite é o stack moderno, tipado, com boa integração
ao Module Federation para microfrontends independentes.

### IV. Infraestrutura: Docker Compose + GitHub Actions

Toda a stack DEVE ser inicializável com um único `docker-compose up`. Cada serviço DEVE
ter seu próprio `Dockerfile` com build multi-stage usando imagens oficiais
(`python:3.11-slim`, `node:20-alpine`). O CI DEVE ser implementado com GitHub Actions
executando lint, type check, testes e build em cada PR. Containers DEVEM rodar com
usuário non-root.

**Rationale**: Um único comando de startup é requisito explícito do desafio. Build multi-stage
reduz tamanho da imagem final. Non-root é baseline inegociável de segurança em containers.

### V. Qualidade: Type Hints, Testes, Linting

Todo código Python DEVE ter type hints completos e passar em `mypy` sem erros.
Todo código TypeScript DEVE compilar sem erros em modo strict (`tsc --noEmit`).
Testes unitários DEVEM ser escritos com Pytest (backend) e React Testing Library (frontend).
Linting DEVE usar Ruff (Python) e ESLint (TypeScript). PRs que introduzem novos
comportamentos sem cobertura de testes NÃO DEVEM ser aprovados sem justificativa
documentada.

**Rationale**: Type hints e linting são a primeira linha de defesa contra bugs. A ausência de
tipos em projetos Python modernos é regressão — inaceitável em código submetido a avaliação.

### VI. Segurança: JWT, LGPD, Validação em Todas as Camadas

Autenticação entre serviços DEVE usar JWT compartilhado. Toda entrada de dados DEVE ser
validada em todas as camadas (Pydantic no backend, Zod ou equivalente no frontend).
Containers DEVEM rodar com usuário non-root (ver Princípio IV). O projeto DEVE seguir as
diretrizes da LGPD: coleta mínima de dados pessoais, finalidade declarada, sem retenção
desnecessária. Secrets NUNCA DEVEM ser commitados — usar `.env` (não versionado) com
`.env.example` documentado.

**Rationale**: JWT é o padrão stateless para autenticação em microserviços. LGPD é
obrigação legal no contexto governamental brasileiro. Validação em todas as camadas
previne injeção e dados corrompidos em qualquer ponto de entrada.

### VII. Observabilidade: Logs Estruturados + Correlation ID + Health Checks

Todos os serviços DEVEM emitir logs estruturados em JSON usando `structlog`. Todo request
DEVE propagar um `X-Request-ID` (Correlation ID) entre serviços via header HTTP. Cada
serviço DEVE expor um endpoint `GET /health` retornando HTTP 200 quando operacional.
Logs DEVEM incluir os campos mínimos: `service`, `level`, `timestamp`, `request_id`.

**Rationale**: Logs estruturados permitem query em ferramentas de observabilidade. Correlation
ID é essencial para rastrear um request através de múltiplos microserviços. Health checks
são pré-requisito para orquestração confiável em qualquer ambiente.

### VIII. Pragmatismo: PMV Funcional Antes de Amplitude

"Um PMV funcional com dois serviços reais vale mais que quatro serviços quebrados."
O projeto DEVE priorizar profundidade sobre largura — features completas e testadas antes
de novas features. Código limpo e legível DEVE ser preferido a código extenso ou sobre-
engenheirado. Complexidade adicional NÃO DEVE ser introduzida sem justificativa em ADR.

**Rationale**: O contexto é um desafio técnico com prazo. Entregar funcionalidade demonstrável
e de qualidade tem mais valor avaliativo do que um escopo amplo e inacabado.

### IX. Documentação: README como Artefato de Primeira Classe

O README DEVE funcionar como documento de onboarding — incluindo setup local, visão de
arquitetura e decisões de design relevantes. Decisões técnicas significativas DEVEM ser
registradas como Architecture Decision Records (ADRs). A documentação da API DEVE ser
gerada automaticamente via Swagger/OpenAPI pelo FastAPI (sem custo de manutenção adicional).
Cada decisão técnica DEVE ser rastreável a um ADR ou comentário no código.

**Rationale**: Avaliadores de desafios técnicos julgam README e documentação com peso
equivalente ao código. ADRs previnem decisões sendo questionadas sem contexto histórico.

### X. IA como Método: Spec-Driven Development

Este projeto adota Spec-Driven Development (SDD) via SpecKit. As especificações em
`.specify/specs/` são a fonte de verdade: o código DEVE ser derivado delas. Toda
contribuição gerada por IA DEVE ser inspecionada e validada pelo engenheiro antes
do commit. O processo de uso de IA DEVE ser transparente e documentado no README.
Especificações NÃO DEVEM ser alteradas para justificar código já escrito — o fluxo
é sempre spec → código, nunca código → spec retroativa.

**Rationale**: SDD garante que decisões de design precedem a implementação, reduzindo
retrabalho. Transparência sobre uso de IA é requisito ético e profissional no contexto
de processo seletivo público.

## Restrições e Padrões Técnicos

- Python DEVE ser >= 3.11; TypeScript DEVE ser >= 5.0; Node.js DEVE ser >= 20 (LTS)
- FastAPI DEVE ser >= 0.100; PostgreSQL DEVE ser >= 15
- Imagens Docker DEVE usar bases oficiais: `python:3.11-slim`, `node:20-alpine`
- Variáveis de ambiente DEVEM ser gerenciadas via `.env` (não versionado) com
  `.env.example` versionado e documentado
- Migrações de banco de dados DEVEM usar Alembic
- Secrets (senhas, tokens, chaves) NUNCA DEVEM aparecer em código ou histórico git
- Cada serviço DEVE ter seu próprio `requirements.txt` ou `pyproject.toml`
- A raiz do repositório DEVE conter um `docker-compose.yml` funcional cobrindo todos
  os serviços

## Fluxo de Desenvolvimento e Quality Gates

### Fluxo por Feature (SpecKit)

1. Criar spec: `/speckit.specify` → `.specify/specs/[###-feature]/spec.md`
2. Gerar plano: `/speckit.plan` → `plan.md`, `research.md`, `data-model.md`, `contracts/`
3. Gerar tasks: `/speckit.tasks` → `tasks.md`
4. Implementar por user story, do P1 ao Pn, validando cada story de forma independente
5. Documentar decisões relevantes em ADR após implementação
6. Verificar quality gates antes de qualquer merge

### Quality Gates (obrigatórios antes de merge)

- [ ] `ruff check .` sem erros (Python)
- [ ] `mypy` sem erros em todos os serviços backend
- [ ] `eslint .` sem erros (TypeScript)
- [ ] `tsc --noEmit` sem erros em todos os MFEs
- [ ] `pytest` passando (backend)
- [ ] Testes React Testing Library passando (frontend)
- [ ] `docker compose build` bem-sucedido para todos os serviços
- [ ] `docker compose up` inicia toda a stack sem erros
- [ ] `GET /health` responde 200 em todos os serviços
- [ ] Sem secrets em texto plano detectados no código

## Governança

Esta constituição é a autoridade máxima sobre as práticas de desenvolvimento deste projeto.
Em caso de conflito entre esta constituição e qualquer outra diretriz, esta constituição
prevalece.

**Processo de emenda**:
1. Propor mudança descrevendo o princípio afetado e a justificativa
2. Atualizar esta constituição via `/speckit.constitution` com a descrição da mudança
3. Propagar impactos para templates afetados (relatório de sync obrigatório)
4. Incrementar versão conforme semver:
   - MAJOR: remoção ou redefinição incompatível de princípio existente
   - MINOR: novo princípio ou seção com orientação material
   - PATCH: clarificação de texto, correção tipográfica, refinamento semântico menor

**Revisão de conformidade**: Todo PR DEVE verificar conformidade mínima com os Princípios
V (Qualidade), VI (Segurança) e VII (Observabilidade) como gates inegociáveis.

**Arquivo de referência para agentes de IA**: `.specify/memory/constitution.md`

**Version**: 1.0.0 | **Ratified**: 2026-03-27 | **Last Amended**: 2026-03-27
