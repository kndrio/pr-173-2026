# Data Model: Order Management Platform MVP

**Branch**: `001-order-mgmt-platform` | **Date**: 2026-03-30

---

## Entidades e Atributos

### User (auth_db)

| Campo | Tipo | Restrições | Descrição |
|-------|------|------------|-----------|
| `id` | UUID | PK, gerado automaticamente | Identificador único |
| `full_name` | VARCHAR(255) | NOT NULL | Nome completo do usuário |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | Endereço de email (login) |
| `hashed_password` | VARCHAR(255) | NOT NULL | Senha em hash bcrypt |
| `role` | ENUM | NOT NULL, default `operator` | Papel: `operator`, `manager`, `admin` |
| `is_active` | BOOLEAN | NOT NULL, default `true` | Status ativo/inativo |
| `created_at` | TIMESTAMPTZ | NOT NULL, default NOW() | Data de criação |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default NOW() | Última atualização |

**Índices**: `email` (UNIQUE, usado no login); `is_active` (filtro na listagem de usuários ativos).

**Validações**:
- `email`: formato válido de email, máximo 255 caracteres
- `full_name`: não vazio, máximo 255 caracteres
- `hashed_password`: derivado de senha com mínimo 8 caracteres (validado antes do hash)
- `role`: apenas valores do enum permitidos

---

### Order (orders_db)

| Campo | Tipo | Restrições | Descrição |
|-------|------|------------|-----------|
| `id` | UUID | PK, gerado automaticamente | Identificador único do pedido |
| `customer_name` | VARCHAR(255) | NOT NULL | Nome do cliente |
| `customer_email` | VARCHAR(255) | NOT NULL | Email do cliente |
| `description` | TEXT | NOT NULL | Descrição do pedido |
| `priority` | ENUM | NOT NULL, default `media` | Prioridade: `baixa`, `media`, `alta`, `urgente` |
| `status` | ENUM | NOT NULL, default `pendente` | Status: `pendente`, `em_andamento`, `concluido`, `cancelado` |
| `notes` | TEXT | NULLABLE | Observações opcionais |
| `total_amount` | NUMERIC(12,2) | NOT NULL, default 0 | Valor total calculado (soma dos itens) |
| `created_by` | UUID | NOT NULL | ID do usuário que criou o pedido |
| `created_at` | TIMESTAMPTZ | NOT NULL, default NOW() | Data de criação |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default NOW() | Última atualização |

**Índices**: `status` (filtro), `priority` (filtro), `created_at DESC` (ordenação padrão), `created_by` (filtro por operador).

**Validações**:
- `customer_email`: formato válido de email
- `customer_name`: não vazio
- `description`: não vazio
- `total_amount`: calculado automaticamente; deve ser >= 0
- `priority`: apenas valores do enum
- `status`: apenas valores do enum; transições validadas na camada de serviço

---

### OrderItem (orders_db)

| Campo | Tipo | Restrições | Descrição |
|-------|------|------------|-----------|
| `id` | UUID | PK, gerado automaticamente | Identificador único do item |
| `order_id` | UUID | FK → Order.id, NOT NULL, ON DELETE CASCADE | Pedido ao qual pertence |
| `name` | VARCHAR(255) | NOT NULL | Nome do produto/serviço |
| `quantity` | INTEGER | NOT NULL, CHECK > 0 | Quantidade |
| `unit_price` | NUMERIC(12,2) | NOT NULL, CHECK >= 0 | Preço unitário em BRL |
| `subtotal` | NUMERIC(12,2) | NOT NULL, COMPUTED | `quantity × unit_price` (armazenado para performance) |

**Validações**:
- `quantity`: inteiro positivo (>= 1)
- `unit_price`: valor não negativo
- `subtotal`: sempre `quantity * unit_price` — nunca editável diretamente
- Pedido deve ter ao menos 1 item (validado na criação)

---

## Diagrama de Relacionamentos

```
auth_db                          orders_db
┌─────────────────┐              ┌─────────────────────┐
│      User       │              │        Order         │
├─────────────────┤              ├─────────────────────┤
│ id (PK)         │              │ id (PK)             │
│ full_name       │              │ customer_name       │
│ email (UNIQUE)  │  created_by  │ customer_email      │
│ hashed_password │◄─────────── │ description         │
│ role            │  (UUID ref,  │ priority            │
│ is_active       │  não FK real)│ status              │
│ created_at      │              │ notes               │
│ updated_at      │              │ total_amount        │
└─────────────────┘              │ created_by          │
                                 │ created_at          │
                                 │ updated_at          │
                                 └──────────┬──────────┘
                                            │ 1:N
                                 ┌──────────▼──────────┐
                                 │      OrderItem       │
                                 ├─────────────────────┤
                                 │ id (PK)             │
                                 │ order_id (FK)       │
                                 │ name                │
                                 │ quantity            │
                                 │ unit_price          │
                                 │ subtotal            │
                                 └─────────────────────┘
```

**Nota**: `created_by` no Orders service armazena o UUID do usuário, mas não é uma foreign key real (bancos separados). A consistência é responsabilidade da camada de aplicação (JWT garante que o UUID existe).

---

## Máquina de Estados — Order.status

```
                   ┌─────────┐
        (criação)  │         │
        ──────────►│pendente │
                   │         │
                   └────┬────┘
                        │ iniciar atendimento
                        ▼
                   ┌────────────┐
                   │            │
                   │em_andamento│
                   │            │
                   └─────┬──────┘
                         │ concluir
                         ▼
                   ┌──────────┐
                   │          │
                   │concluido │  (estado final — sem saída)
                   │          │
                   └──────────┘

     cancelado ◄── qualquer estado (exceto cancelado e concluido)
     ┌──────────┐
     │          │
     │cancelado │  (estado final — sem saída)
     │          │
     └──────────┘
```

**Transições válidas**:
- `pendente` → `em_andamento`
- `em_andamento` → `concluido`
- `pendente` → `cancelado`
- `em_andamento` → `cancelado`
- Qualquer transição não listada acima é rejeitada com erro HTTP 422

---

## Regras de Cálculo

### total_amount do Pedido

```
Order.total_amount = Σ (item.quantity × item.unit_price) para cada item do pedido
```

- Calculado automaticamente na criação do pedido.
- Recalculado se itens forem adicionados/removidos (não previsto no MVP — itens são imutáveis após criação).
- Armazenado como `NUMERIC(12,2)` — até R$ 9.999.999.999,99.

### subtotal do Item

```
OrderItem.subtotal = OrderItem.quantity × OrderItem.unit_price
```

- Armazenado para evitar recálculo em queries de listagem.
- Sempre mantido em sync com `quantity` e `unit_price` (campos imutáveis após criação no MVP).

---

## Schemas de Validação (Pydantic — Backend)

### UserCreate
```python
class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
```

### UserLogin
```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str
```

### OrderItemCreate
```python
class OrderItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0, decimal_places=2)
```

### OrderCreate
```python
class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: EmailStr
    description: str = Field(min_length=1)
    items: list[OrderItemCreate] = Field(min_length=1)
    priority: Priority = Priority.media
    notes: str | None = None
```

### OrderStatusUpdate
```python
class OrderStatusUpdate(BaseModel):
    status: OrderStatus

    @model_validator(mode='after')
    def validate_transition(self) -> 'OrderStatusUpdate':
        # Validação de transição feita no service layer com o status atual
        return self
```

---

## Schemas de Validação (Zod — Frontend)

### orderItemSchema
```typescript
const orderItemSchema = z.object({
  name: z.string().min(1, 'Nome do item é obrigatório'),
  quantity: z.number().int().positive('Quantidade deve ser maior que zero'),
  unit_price: z.number().nonnegative('Preço não pode ser negativo'),
})
```

### orderCreateSchema
```typescript
const orderCreateSchema = z.object({
  customer_name: z.string().min(1, 'Nome do cliente é obrigatório'),
  customer_email: z.string().email('Email inválido'),
  description: z.string().min(1, 'Descrição é obrigatória'),
  items: z.array(orderItemSchema).min(1, 'Adicione ao menos um item'),
  priority: z.enum(['baixa', 'media', 'alta', 'urgente']).default('media'),
  notes: z.string().optional(),
})
```

### loginSchema
```typescript
const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Senha deve ter no mínimo 8 caracteres'),
})
```
