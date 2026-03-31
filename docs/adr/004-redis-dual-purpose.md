# ADR-004: Redis para Cache e Pub/Sub (Dual-Purpose)

**Status**: Aceito  
**Data**: 2026-03-27  
**Autores**: Kennedy Carvalho

---

## Contexto

O `orders-service` tem dois requisitos distintos de infraestrutura:

1. **Cache de listagens**: `GET /pedidos` com filtros e paginação é potencialmente
   custoso (full table scan com COUNT). Resultado deve ser cacheado para evitar
   queries repetidas.

2. **Eventos de domínio**: quando um pedido é criado ou atualizado, outros sistemas
   (futura auditoria, notificações, analytics) precisam ser notificados de forma
   assíncrona e desacoplada.

As opções são: Redis (cache + Pub/Sub), Memcached (cache only) + mensageria separada,
ou Kafka/RabbitMQ como mensageria dedicada.

---

## Decisão

Adotar **Redis 7** para ambos os casos de uso no `orders-service`.

- **Cache**: chaves `orders:list:{page}:{page_size}:{status}:{priority}` com TTL
  de 5 minutos (configurável via `REDIS_CACHE_TTL`). Invalidação por padrão com
  `SCAN + DEL orders:list:*` — sem uso de `KEYS *` para evitar bloqueio do servidor.

- **Pub/Sub**: canal `orders` recebe eventos JSON com `event_type`, `order_id` e
  dados relevantes na criação e atualização de pedidos.

**Por que não Kafka para PMV:**

| Critério | Redis Pub/Sub | Kafka |
|----------|--------------|-------|
| Setup | 1 container, config zero | ZooKeeper + Broker + Schema Registry |
| Latência | < 1ms | ~10ms |
| Durabilidade | Não (fire-and-forget) | Sim (log persistente) |
| Ordenação | Por canal | Por partição |
| Replay | Não | Sim |
| Operação | Zero | Alto |

Para um PMV sem consumidores de eventos implementados, Kafka adiciona 3 containers
e complexidade operacional significativa sem benefício demonstrável. Redis já é
requisito para cache — usar Pub/Sub é aproveitar infraestrutura existente.

---

## Consequências

### Positivas

- **Um componente, dois requisitos**: Redis já está no `docker-compose.yml` para
  cache; Pub/Sub é gratuito em termos de infraestrutura.
- **Simplicidade operacional**: `redis:7-alpine` é um container stateless sem
  configuração adicional. Health check trivial com `redis-cli ping`.
- **Performance**: cache com TTL reduz latência da listagem de ~200ms para < 5ms
  nas requisições subsequentes dentro da janela de TTL.
- **Desacoplamento real**: eventos Pub/Sub já habilitam futuros consumidores
  (audit log, notificações) sem mudança no `orders-service`.

### Negativas

- **Sem durabilidade para eventos**: se um consumidor estiver offline no momento
  da publicação, o evento é perdido. Redis Pub/Sub é fire-and-forget.
- **Sem replay**: não é possível reprocessar eventos históricos — decisão
  arquitetural que precisaria ser revisada antes de implementar auditoria.
- **Cache compartilhado por usuário**: o cache atual é global por query params,
  não por usuário. Se isolamento por usuário for necessário, as chaves de cache
  precisam incluir `user_id`.

### Critério de migração para Kafka

Migrar para Kafka/RabbitMQ quando: (1) houver requisito de replay de eventos,
(2) houver mais de 3 consumidores distintos, ou (3) a perda de eventos tiver
impacto de negócio mensurável (auditoria obrigatória, por exemplo).
