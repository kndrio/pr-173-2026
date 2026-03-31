# ADR-005: Integração com IA — Claude API com Fallback por Regras

**Status**: Aceito  
**Data**: 2026-03-30  
**Autores**: Kennedy Carvalho

---

## Contexto

O desafio inclui como bônus a análise de pedidos por inteligência artificial.
O requisito é sugerir prioridade e fornecer resumo executivo de um pedido com
base nos seus dados (valor, itens, descrição, status).

As opções são:

1. **Modelo ML local** (scikit-learn, transformers): requer treinamento com dados
   rotulados, infraestrutura de inferência, versionamento de modelo. Sem dados
   históricos reais, o modelo seria trivial ou inútil.

2. **API de LLM** (Claude, GPT-4, Qwen): zero infraestrutura de modelo, prompt engineering
   direto, resposta em linguagem natural. Custo por requisição, dependência externa.

3. **Regras determinísticas**: fallback simples baseado em valor total e quantidade
   de itens. Sem dependência externa, sem custo, previsível.

---

## Decisão

Adotar API pollinations.ai como análise primária com
**fallback automático por regras** quando a API não estiver disponível.

**Arquitetura do endpoint** (`POST /pedidos/{order_id}/ai-analysis`):

1. Busca o pedido no banco (404 se inexistente)
2. Se `API_KEY` não configurada → fallback imediato
3. Chama `gen.pollinations.ai` via httpx async (timeout 30s)
4. Parse da resposta JSON; validação via Pydantic (`suggested_priority: Priority`)
5. Em qualquer exceção → fallback por regras (nunca 5xx)

**Regras de fallback:**
- Valor > R$ 10.000 → `urgente`
- Valor > R$ 5.000 → `alta`
- Default → `media`
- Se itens > 3 → eleva um nível (até `urgente`)

**Prompt engineering:**
```
System: "Você é um analista de pedidos governamentais. Analise os dados
do pedido e retorne APENAS um JSON com: suggested_priority
(baixa/media/alta/urgente), executive_summary (resumo executivo em
português, max 3 frases), observations (lista de até 3 observações
relevantes)."
```

Dados enviados: `id`, `customer_name`, `description`, `total_amount`,
`status`, `priority`, `items`, `notes`. `customer_email` e `created_by`
excluídos por minimização de dados (LGPD).

**Por que  pollinations.ai e não Claude (Anthropic) GPT-4 (Openai):**
O desafio técnico apresenta integração com IA como um bônus.
Qwen-safety é um modelo free-tier da Polinations que permite o uso sem custo neste demo.

---

## Consequências

### Positivas

- **Resiliência total**: o endpoint nunca retorna 5xx por falha de IA. Fallback
  transparente garante UX consistente independente de disponibilidade da API.
- **Zero infraestrutura de modelo**: sem GPU, sem servidor de inferência, sem
  pipeline de treinamento. A análise funciona desde o primeiro deploy.
- **Qualidade de linguagem natural**: o LLM produz resumos executivos em português
  adequados ao contexto governamental — algo que regras determinísticas não conseguem.
- **`model_used` rastreável**: a resposta indica `"claude-sonnet-4-20250514"` ou
  `"rule-based-fallback"`, permitindo auditoria de qual análise usou IA real.
- **`suggested_priority` validado**: tipo `Priority` (enum) no Pydantic garante que
  output inválido da IA não passa para a resposta — cai no fallback.

### Negativas

- **Custo por requisição**: cada análise consome tokens da API Anthropic. Sem rate
  limiting por usuário, um ator mal-intencionado pode gerar custo elevado.
  *Mitigação documentada no código; implementação completa em produção.*
- **Dependência externa**: disponibilidade da análise IA depende de uptime da
  Anthropic API. Fallback mitiga o impacto mas não elimina a dependência.
- **Prompt injection**: campos `description` e `notes` são texto livre do usuário
  e são enviados ao LLM. A resposta é consumida apenas pelo Pydantic (sem exec/eval),
  portanto o risco de injeção com impacto sistêmico é baixo — mas existe.
- **Não determinístico**: o mesmo pedido pode receber análises diferentes em
  requisições distintas. Aceitável para sugestão de prioridade; inaceitável para
  decisão final automatizada sem revisão humana.

### Decisão de segurança associada

`except Exception` no handler da API foi substituído por handlers específicos
(`httpx.HTTPError`, `json.JSONDecodeError | KeyError`, fallback genérico) para
evitar que `str(exc)` em HTTP errors reflita o conteúdo da resposta da API
(potencialmente sensível) nos logs de aplicação.
