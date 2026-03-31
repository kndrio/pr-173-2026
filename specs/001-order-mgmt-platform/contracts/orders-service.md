# API Contract: Orders Service

**Base URL**: `http://localhost:8002` (direct) | `/api/orders` (via NGINX proxy)
**OpenAPI docs**: `GET /docs`
**Version**: v1

---

## Endpoints

### POST /api/v1/orders

Cria um novo pedido.

**Headers**: `Authorization: Bearer <token>`

**Request Body** (application/json):
```json
{
  "customer_name": "Maria Santos",
  "customer_email": "maria@cliente.com",
  "description": "Pedido de material de escritório para o departamento de TI",
  "items": [
    {
      "name": "Notebook Dell Inspiron",
      "quantity": 2,
      "unit_price": 3500.00
    },
    {
      "name": "Mouse sem fio",
      "quantity": 5,
      "unit_price": 89.90
    }
  ],
  "priority": "alta",
  "notes": "Entrega urgente — sala 302"
}
```

**Validações**:
- `customer_name`: obrigatório, não vazio
- `customer_email`: formato de email válido
- `description`: obrigatório, não vazio
- `items`: ao menos 1 item; cada item com `quantity >= 1` e `unit_price >= 0`
- `priority`: `baixa` | `media` | `alta` | `urgente` (default: `media`)

**Response 201** (Created):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "customer_name": "Maria Santos",
  "customer_email": "maria@cliente.com",
  "description": "Pedido de material de escritório para o departamento de TI",
  "items": [
    {
      "id": "item-uuid-1",
      "name": "Notebook Dell Inspiron",
      "quantity": 2,
      "unit_price": 3500.00,
      "subtotal": 7000.00
    },
    {
      "id": "item-uuid-2",
      "name": "Mouse sem fio",
      "quantity": 5,
      "unit_price": 89.90,
      "subtotal": 449.50
    }
  ],
  "priority": "alta",
  "status": "pendente",
  "notes": "Entrega urgente — sala 302",
  "total_amount": 7449.50,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-03-30T10:00:00Z",
  "updated_at": "2026-03-30T10:00:00Z"
}
```

**Response 422** (Validation Error):
```json
{
  "detail": [
    {
      "loc": ["body", "items"],
      "msg": "List should have at least 1 item after validation",
      "type": "too_short"
    }
  ]
}
```

---

### GET /api/v1/orders

Lista pedidos com paginação e filtros.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `page` | integer | 1 | Número da página (>= 1) |
| `page_size` | integer | 20 | Itens por página (1-100) |
| `status` | string | (todos) | Filtro: `pendente` \| `em_andamento` \| `concluido` \| `cancelado` |
| `priority` | string | (todos) | Filtro: `baixa` \| `media` \| `alta` \| `urgente` |
| `sort` | string | `created_at_desc` | Ordenação: `created_at_desc` \| `created_at_asc` |

**Response 200** (OK):
```json
{
  "items": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "customer_name": "Maria Santos",
      "customer_email": "maria@cliente.com",
      "description": "Pedido de material de escritório...",
      "priority": "alta",
      "status": "pendente",
      "total_amount": 7449.50,
      "created_by": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-03-30T10:00:00Z",
      "updated_at": "2026-03-30T10:00:00Z"
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 20,
  "pages": 8,
  "filters": {
    "status_counts": {
      "pendente": 45,
      "em_andamento": 32,
      "concluido": 67,
      "cancelado": 12
    },
    "priority_counts": {
      "baixa": 23,
      "media": 78,
      "alta": 41,
      "urgente": 14
    }
  }
}
```

**Nota**: Listagem servida do cache Redis (TTL 5min). Itens não incluídos na listagem — apenas no detalhe.

---

### GET /api/v1/orders/{order_id}

Retorna dados completos de um pedido específico.

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**: `order_id` (UUID)

**Response 200** (OK):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "customer_name": "Maria Santos",
  "customer_email": "maria@cliente.com",
  "description": "Pedido de material de escritório para o departamento de TI",
  "items": [
    {
      "id": "item-uuid-1",
      "name": "Notebook Dell Inspiron",
      "quantity": 2,
      "unit_price": 3500.00,
      "subtotal": 7000.00
    },
    {
      "id": "item-uuid-2",
      "name": "Mouse sem fio",
      "quantity": 5,
      "unit_price": 89.90,
      "subtotal": 449.50
    }
  ],
  "priority": "alta",
  "status": "pendente",
  "notes": "Entrega urgente — sala 302",
  "total_amount": 7449.50,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-03-30T10:00:00Z",
  "updated_at": "2026-03-30T10:00:00Z"
}
```

**Response 404** (Not Found):
```json
{
  "detail": "Order not found"
}
```

---

### PATCH /api/v1/orders/{order_id}/status

Atualiza o status de um pedido. Valida transição antes de aplicar.

**Headers**: `Authorization: Bearer <token>`

**Request Body** (application/json):
```json
{
  "status": "em_andamento"
}
```

**Response 200** (OK — retorna pedido atualizado, sem itens):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "em_andamento",
  "updated_at": "2026-03-30T10:05:00Z"
}
```

**Response 422** (Transição inválida):
```json
{
  "detail": "Invalid status transition: concluido → em_andamento"
}
```

**Response 404** (Not Found):
```json
{
  "detail": "Order not found"
}
```

**Efeito colateral**: Invalida cache Redis (`orders:list:*`). Publica evento `order_updated` no canal Redis Pub/Sub `orders`.

---

### POST /api/v1/orders/{order_id}/analyze

Analisa o pedido com IA e retorna sugestão de prioridade + resumo executivo.

**Headers**: `Authorization: Bearer <token>`

**Request Body**: nenhum (dados do pedido são buscados pelo próprio endpoint)

**Response 200** (OK — análise via IA ou fallback):
```json
{
  "suggested_priority": "alta",
  "executive_summary": "Pedido de equipamentos de TI de alto valor (R$ 7.449,50) com 2 itens para o departamento de TI. O valor total e a natureza dos itens indicam prioridade alta. Recomenda-se verificar disponibilidade de fornecedor antes de iniciar o atendimento.",
  "analysis_source": "ai",
  "analyzed_at": "2026-03-30T10:10:00Z"
}
```

**Campo `analysis_source`**: `"ai"` (análise pelo serviço inteligente) ou `"rules"` (fallback por regras).

**Response 404** (Pedido não encontrado):
```json
{
  "detail": "Order not found"
}
```

**Nota**: Mesmo em caso de timeout/falha do serviço externo, responde 200 com `analysis_source: "rules"`. Nunca retorna 503.

---

### GET /health

Health check do serviço.

**Response 200** (OK):
```json
{
  "status": "healthy",
  "service": "orders-service",
  "database": "connected",
  "redis": "connected"
}
```

---

## Eventos Redis Pub/Sub

**Canal**: `orders`

### order_created
```json
{
  "event": "order_created",
  "order_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "customer_name": "Maria Santos",
  "priority": "alta",
  "total_amount": 7449.50,
  "timestamp": "2026-03-30T10:00:00Z"
}
```

### order_updated
```json
{
  "event": "order_updated",
  "order_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "previous_status": "pendente",
  "new_status": "em_andamento",
  "timestamp": "2026-03-30T10:05:00Z"
}
```

---

## Autenticação

Todos os endpoints (exceto `/health`) requerem:
```
Authorization: Bearer <JWT_TOKEN>
```

O serviço valida o JWT usando o `JWT_SECRET` compartilhado com o auth-service. Token expirado retorna HTTP 401.

---

## Cabeçalhos Obrigatórios

| Header | Descrição |
|--------|-----------|
| `Content-Type: application/json` | Para requests com body |
| `X-Request-ID: <uuid>` | Opcional; gerado pelo serviço se ausente; propagado nos logs |

---

## Erros Comuns

| HTTP Status | Situação |
|-------------|----------|
| 401 | Token ausente, inválido ou expirado |
| 404 | Pedido não encontrado |
| 422 | Falha de validação ou transição de status inválida |
| 500 | Erro inesperado do servidor |
