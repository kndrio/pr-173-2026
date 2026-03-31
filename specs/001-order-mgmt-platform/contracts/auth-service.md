# API Contract: Auth Service

**Base URL**: `http://localhost:8001` (direct) | `/api/auth` (via NGINX proxy)
**OpenAPI docs**: `GET /docs`
**Version**: v1

---

## Endpoints

### POST /api/v1/auth/register

Registra um novo usuário na plataforma.

**Request Body** (application/json):
```json
{
  "full_name": "João da Silva",
  "email": "joao@empresa.com",
  "password": "senha123!"
}
```

**Validações**:
- `full_name`: obrigatório, não vazio
- `email`: formato de email válido, único no sistema
- `password`: mínimo 8 caracteres

**Response 201** (Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "João da Silva",
  "email": "joao@empresa.com",
  "role": "operator",
  "is_active": true,
  "created_at": "2026-03-30T10:00:00Z"
}
```

**Response 409** (Conflict — email já existe):
```json
{
  "detail": "Email already registered"
}
```

**Response 422** (Validation Error):
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "type": "string_too_short"
    }
  ]
}
```

---

### POST /api/v1/auth/login

Autentica um usuário e retorna token JWT.

**Request Body** (application/json):
```json
{
  "email": "joao@empresa.com",
  "password": "senha123!"
}
```

**Response 200** (OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**JWT Payload**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "joao@empresa.com",
  "role": "operator",
  "exp": 1743340800
}
```

**Response 401** (Unauthorized):
```json
{
  "detail": "Invalid credentials"
}
```

---

### GET /api/v1/auth/me

Retorna dados do usuário autenticado.

**Headers**: `Authorization: Bearer <token>`

**Response 200** (OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "João da Silva",
  "email": "joao@empresa.com",
  "role": "operator",
  "is_active": true,
  "created_at": "2026-03-30T10:00:00Z"
}
```

**Response 401** (Unauthorized — token inválido ou expirado):
```json
{
  "detail": "Could not validate credentials"
}
```

---

### GET /api/v1/users

Lista usuários ativos com paginação.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `page` | integer | 1 | Número da página (>= 1) |
| `page_size` | integer | 20 | Itens por página (1-100) |

**Response 200** (OK):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "João da Silva",
      "email": "joao@empresa.com",
      "role": "operator",
      "is_active": true,
      "created_at": "2026-03-30T10:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

---

### GET /health

Health check do serviço.

**Response 200** (OK):
```json
{
  "status": "healthy",
  "service": "auth-service",
  "database": "connected"
}
```

---

## Autenticação

Todos os endpoints (exceto `/register`, `/login`, e `/health`) requerem:
```
Authorization: Bearer <JWT_TOKEN>
```

Token expirado retorna HTTP 401. O frontend deve redirecionar para `/login` automaticamente.

---

## Cabeçalhos Obrigatórios

| Header | Descrição |
|--------|-----------|
| `Content-Type: application/json` | Para requests com body |
| `X-Request-ID: <uuid>` | Opcional; gerado pelo serviço se ausente |

---

## Erros Comuns

| HTTP Status | Código | Situação |
|-------------|--------|----------|
| 400 | Bad Request | Body malformado (JSON inválido) |
| 401 | Unauthorized | Token ausente, inválido ou expirado |
| 409 | Conflict | Email já cadastrado |
| 422 | Unprocessable Entity | Falha de validação dos campos |
| 500 | Internal Server Error | Erro inesperado do servidor |
