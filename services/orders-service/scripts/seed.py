"""
Seed script — populates auth_db (users) and orders_db (orders) via the service APIs.

Usage (inside container):
    python scripts/seed.py

Environment variables (defaults work in Docker Compose):
    AUTH_URL   — auth-service base URL  (default: http://auth-service:8001)
    ORDERS_URL — orders-service base URL (default: http://orders-service:8002)
"""
import asyncio
import os
import random
import sys

import httpx

AUTH_URL = os.getenv("AUTH_URL", "http://auth-service:8001")
ORDERS_URL = os.getenv("ORDERS_URL", "http://orders-service:8002")

# ──────────────────────────────────────────────
# Seed data
# ──────────────────────────────────────────────

USERS = [
    {"full_name": "Administrador Sistema", "email": "admin@gov.br", "password": "Teste@123"},
    {"full_name": "Operador Pedidos", "email": "operador@gov.br", "password": "Teste@123"},
    {"full_name": "Visualizador", "email": "viewer@gov.br", "password": "Teste@123"},
]

SAMPLE_ORDERS = [
    {
        "customer_name": "Ministério da Saúde",
        "customer_email": "compras@saude.gov.br",
        "description": "Aquisição de EPIs para unidades de saúde",
        "priority": "urgente",
        "notes": "Entrega em até 48h",
        "items": [
            {"name": "Máscara N95", "quantity": 500, "unit_price": "12.50"},
            {"name": "Luva Nitrílica caixa 100un", "quantity": 200, "unit_price": "45.00"},
            {"name": "Avental descartável", "quantity": 300, "unit_price": "8.90"},
        ],
        "target_status": "em_andamento",
    },
    {
        "customer_name": "Secretaria de Educação SP",
        "customer_email": "licitacao@educacao.sp.gov.br",
        "description": "Material didático para ensino fundamental",
        "priority": "alta",
        "items": [
            {"name": "Livro Matemática 5º ano", "quantity": 1000, "unit_price": "32.00"},
            {"name": "Caderno 96 folhas", "quantity": 2000, "unit_price": "8.50"},
        ],
        "target_status": "pendente",
    },
    {
        "customer_name": "Câmara Municipal de Recife",
        "customer_email": "compras@camararecife.pe.gov.br",
        "description": "Equipamentos de informática para modernização",
        "priority": "media",
        "items": [
            {"name": "Monitor 24 polegadas Full HD", "quantity": 20, "unit_price": "890.00"},
            {"name": "Teclado e Mouse sem fio", "quantity": 20, "unit_price": "185.00"},
            {"name": "Cabo HDMI 2m", "quantity": 25, "unit_price": "35.00"},
        ],
        "target_status": "concluido",
    },
    {
        "customer_name": "Prefeitura de Manaus",
        "customer_email": "pregao@manaus.am.gov.br",
        "description": "Serviços de limpeza para prédios públicos",
        "priority": "baixa",
        "notes": "Contrato trimestral",
        "items": [
            {"name": "Detergente 5L galão", "quantity": 100, "unit_price": "18.90"},
            {"name": "Desinfetante 5L galão", "quantity": 80, "unit_price": "22.00"},
        ],
        "target_status": "cancelado",
    },
    {
        "customer_name": "INSS Nacional",
        "customer_email": "aquisicoes@inss.gov.br",
        "description": "Mobiliário para nova agência",
        "priority": "alta",
        "items": [
            {"name": "Cadeira ergonômica giratória", "quantity": 30, "unit_price": "620.00"},
            {"name": "Mesa de trabalho L 160cm", "quantity": 15, "unit_price": "950.00"},
            {"name": "Armário 2 portas", "quantity": 10, "unit_price": "480.00"},
            {"name": "Gaveteiro 3 gavetas", "quantity": 20, "unit_price": "310.00"},
        ],
        "target_status": "em_andamento",
    },
    {
        "customer_name": "Tribunal de Justiça RJ",
        "customer_email": "compras@tjrj.jus.br",
        "description": "Papel A4 e materiais de escritório",
        "priority": "baixa",
        "items": [
            {"name": "Papel A4 75g resma 500fls", "quantity": 500, "unit_price": "28.00"},
            {"name": "Caneta esferográfica azul caixa 50un", "quantity": 20, "unit_price": "42.00"},
            {"name": "Grampeador 26/6", "quantity": 10, "unit_price": "35.00"},
        ],
        "target_status": "concluido",
    },
    {
        "customer_name": "Universidade Federal de Minas Gerais",
        "customer_email": "licitacoes@ufmg.br",
        "description": "Reagentes químicos para laboratório",
        "priority": "urgente",
        "notes": "Aprovação da ANVISA requerida",
        "items": [
            {"name": "Ácido Clorídrico P.A. 1L", "quantity": 50, "unit_price": "85.00"},
            {"name": "Etanol 95% 1L", "quantity": 100, "unit_price": "42.00"},
        ],
        "target_status": "pendente",
    },
    {
        "customer_name": "Banco do Brasil",
        "customer_email": "compras@bb.com.br",
        "description": "Uniformes para equipe de atendimento",
        "priority": "media",
        "items": [
            {"name": "Camisa social manga longa P", "quantity": 50, "unit_price": "95.00"},
            {"name": "Camisa social manga longa M", "quantity": 80, "unit_price": "95.00"},
            {"name": "Camisa social manga longa G", "quantity": 60, "unit_price": "95.00"},
            {"name": "Gravata institucional", "quantity": 190, "unit_price": "45.00"},
        ],
        "target_status": "pendente",
    },
    {
        "customer_name": "Petrobras Logística",
        "customer_email": "suprimentos@petrobras.com.br",
        "description": "Ferramentas industriais para manutenção",
        "priority": "alta",
        "items": [
            {"name": "Chave torquímetro 0-100Nm", "quantity": 5, "unit_price": "1250.00"},
            {"name": "Multímetro digital", "quantity": 10, "unit_price": "380.00"},
        ],
        "target_status": "em_andamento",
    },
    {
        "customer_name": "Secretaria de Segurança Pública BA",
        "customer_email": "logistica@ssp.ba.gov.br",
        "description": "Combustível para frota de veículos policiais",
        "priority": "urgente",
        "items": [
            {"name": "Gasolina comum litro", "quantity": 5000, "unit_price": "5.89"},
        ],
        "target_status": "concluido",
    },
    {
        "customer_name": "Hospital das Clínicas SP",
        "customer_email": "farmacia@hcsp.org.br",
        "description": "Medicamentos essenciais estoque emergência",
        "priority": "urgente",
        "notes": "Código CATMAT: 389154",
        "items": [
            {"name": "Paracetamol 750mg caixa 100cp", "quantity": 200, "unit_price": "18.50"},
            {"name": "Ibuprofeno 600mg caixa 30cp", "quantity": 150, "unit_price": "22.00"},
            {"name": "Dipirona 500mg/mL frasco 100mL", "quantity": 500, "unit_price": "9.80"},
        ],
        "target_status": "pendente",
    },
    {
        "customer_name": "Correios",
        "customer_email": "almoxarifado@correios.com.br",
        "description": "Caixas de papelão e embalagens para postagem",
        "priority": "media",
        "items": [
            {"name": "Caixa Sedex 1 (16x11x6cm) pct 25un", "quantity": 200, "unit_price": "38.00"},
            {"name": "Caixa Sedex 2 (24x16x8cm) pct 25un", "quantity": 150, "unit_price": "52.00"},
            {"name": "Fita adesiva 45mm x 45m", "quantity": 100, "unit_price": "12.50"},
        ],
        "target_status": "cancelado",
    },
]


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

async def register_user(client: httpx.AsyncClient, user: dict) -> None:
    resp = await client.post(
        f"{AUTH_URL}/api/v1/auth/register",
        json=user,
        timeout=10.0,
    )
    if resp.status_code == 201:
        print(f"  ✓ Criado: {user['email']}")
    elif resp.status_code == 409:
        print(f"  → Já existe: {user['email']}")
    else:
        print(f"  ✗ Erro ao criar {user['email']}: {resp.status_code} {resp.text}")


async def get_token(client: httpx.AsyncClient, email: str, password: str) -> str:
    resp = await client.post(
        f"{AUTH_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


async def count_orders(client: httpx.AsyncClient, token: str) -> int:
    resp = await client.get(
        f"{ORDERS_URL}/pedidos",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()["total_count"]


async def create_order(client: httpx.AsyncClient, token: str, order: dict) -> str | None:
    payload = {k: v for k, v in order.items() if k != "target_status"}
    resp = await client.post(
        f"{ORDERS_URL}/pedidos",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    if resp.status_code == 201:
        return resp.json()["id"]
    print(f"  ✗ Erro ao criar pedido '{order['description'][:40]}': {resp.status_code} {resp.text}")
    return None


async def advance_status(
    client: httpx.AsyncClient, token: str, order_id: str, target: str
) -> None:
    """Drive the status machine: pendente → em_andamento → concluido/cancelado."""
    transitions = {
        "em_andamento": ["em_andamento"],
        "concluido": ["em_andamento", "concluido"],
        "cancelado": ["cancelado"],
    }
    for next_status in transitions.get(target, []):
        resp = await client.patch(
            f"{ORDERS_URL}/pedidos/{order_id}",
            json={"status": next_status},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        if resp.status_code not in (200, 422):
            print(f"  ✗ Erro transição {next_status}: {resp.status_code}")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

async def main() -> None:
    print("━━━ Seed: Pedidos Platform ━━━")

    async with httpx.AsyncClient() as client:
        # Step 1 — Users
        print("\n[1/3] Criando usuários...")
        for user in USERS:
            await register_user(client, user)

        # Step 2 — Token (use operador for order creation)
        print("\n[2/3] Autenticando como operador@gov.br...")
        token = await get_token(client, "operador@gov.br", "Teste@123")
        print("  ✓ Token obtido")

        # Step 3 — Orders (idempotent check)
        existing = await count_orders(client, token)
        if existing >= len(SAMPLE_ORDERS):
            print(f"\n[3/3] {existing} pedidos já existem — nenhum novo criado.")
        else:
            print(f"\n[3/3] Criando {len(SAMPLE_ORDERS)} pedidos...")
            for order in SAMPLE_ORDERS:
                order_id = await create_order(client, token, order)
                if order_id and order.get("target_status", "pendente") != "pendente":
                    await advance_status(client, token, order_id, order["target_status"])
                    print(f"  ✓ Pedido criado → {order['target_status']}: {order['description'][:50]}")
                elif order_id:
                    print(f"  ✓ Pedido criado (pendente): {order['description'][:50]}")

    print("\n✅ Seed concluído!\n")
    print("Usuários de acesso:")
    for u in USERS:
        print(f"  {u['email']} / {u['password']}")


if __name__ == "__main__":
    asyncio.run(main())
