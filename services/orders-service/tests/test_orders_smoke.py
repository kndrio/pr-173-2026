"""Smoke tests for orders endpoints — Constitution V compliance for Phase 2."""
import pytest
from httpx import AsyncClient


ORDER_PAYLOAD = {
    "customer_name": "João Silva",
    "customer_email": "joao@example.com",
    "description": "Pedido de teste",
    "items": [
        {"name": "Produto A", "quantity": 2, "unit_price": 50.00},
        {"name": "Produto B", "quantity": 1, "unit_price": 30.00},
    ],
    "priority": "alta",
}


@pytest.mark.asyncio
async def test_create_order_with_correct_total(client: AsyncClient) -> None:
    """Creating an order computes total_amount = sum of item subtotals."""
    response = await client.post("/api/v1/orders", json=ORDER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "João Silva"
    # 2 * 50.00 + 1 * 30.00 = 130.00
    assert float(data["total_amount"]) == pytest.approx(130.00)
    assert data["status"] == "pendente"
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_orders(client: AsyncClient) -> None:
    """After creating an order, listing returns it in results."""
    # Create one order first
    create_resp = await client.post("/api/v1/orders", json=ORDER_PAYLOAD)
    assert create_resp.status_code == 201

    response = await client.get("/api/v1/orders")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_valid_status_transition(client: AsyncClient) -> None:
    """pendente → em_andamento is a valid transition."""
    # Create order
    create_resp = await client.post("/api/v1/orders", json=ORDER_PAYLOAD)
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]

    # Transition: pendente → em_andamento
    patch_resp = await client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "em_andamento"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "em_andamento"


@pytest.mark.asyncio
async def test_invalid_status_transition_returns_422(client: AsyncClient) -> None:
    """concluido → em_andamento is invalid; should return 422."""
    # Create and move to concluido
    create_resp = await client.post("/api/v1/orders", json=ORDER_PAYLOAD)
    order_id = create_resp.json()["id"]
    await client.patch(f"/api/v1/orders/{order_id}/status", json={"status": "em_andamento"})
    await client.patch(f"/api/v1/orders/{order_id}/status", json={"status": "concluido"})

    # Attempt invalid transition
    patch_resp = await client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "em_andamento"},
    )
    assert patch_resp.status_code == 422
    assert "Invalid status transition" in patch_resp.json()["detail"]
