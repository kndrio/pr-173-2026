"""Smoke tests for orders endpoints — Constitution V compliance."""
import pytest
from httpx import AsyncClient


ORDER_PAYLOAD = {
    "customer_name": "João Silva",
    "customer_email": "joao@example.com",
    "description": "Pedido de teste",
    "items": [
        {"name": "Produto A", "quantity": 2, "unit_price": "50.00"},
        {"name": "Produto B", "quantity": 1, "unit_price": "30.00"},
    ],
    "priority": "alta",
}


@pytest.mark.asyncio
async def test_create_order_with_correct_total(client: AsyncClient) -> None:
    """POST /pedidos — total_amount = sum of item subtotals, status defaults to pendente."""
    response = await client.post("/pedidos", json=ORDER_PAYLOAD)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["customer_name"] == "João Silva"
    # 2 * 50.00 + 1 * 30.00 = 130.00
    assert float(data["total_amount"]) == pytest.approx(130.00)
    assert data["status"] == "pendente"
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_orders(client: AsyncClient) -> None:
    """GET /pedidos — returns list with at least the created order."""
    await client.post("/pedidos", json=ORDER_PAYLOAD)

    response = await client.get("/pedidos")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] >= 1


@pytest.mark.asyncio
async def test_get_order_by_id(client: AsyncClient) -> None:
    """GET /pedidos/{id} — returns full order with items."""
    create_resp = await client.post("/pedidos", json=ORDER_PAYLOAD)
    order_id = create_resp.json()["id"]

    response = await client.get(f"/pedidos/{order_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == order_id
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_order_not_found(client: AsyncClient) -> None:
    """GET /pedidos/{nonexistent_id} — returns 404."""
    import uuid
    response = await client.get(f"/pedidos/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_valid_status_transition(client: AsyncClient) -> None:
    """PATCH /pedidos/{id} — pendente → em_andamento is valid."""
    create_resp = await client.post("/pedidos", json=ORDER_PAYLOAD)
    order_id = create_resp.json()["id"]

    patch_resp = await client.patch(f"/pedidos/{order_id}", json={"status": "em_andamento"})
    assert patch_resp.status_code == 200, patch_resp.text
    assert patch_resp.json()["status"] == "em_andamento"


@pytest.mark.asyncio
async def test_invalid_status_transition_returns_422(client: AsyncClient) -> None:
    """PATCH /pedidos/{id} — concluido → em_andamento must return 422."""
    create_resp = await client.post("/pedidos", json=ORDER_PAYLOAD)
    order_id = create_resp.json()["id"]

    await client.patch(f"/pedidos/{order_id}", json={"status": "em_andamento"})
    await client.patch(f"/pedidos/{order_id}", json={"status": "concluido"})

    patch_resp = await client.patch(f"/pedidos/{order_id}", json={"status": "em_andamento"})
    assert patch_resp.status_code == 422
    assert "Invalid status transition" in patch_resp.json()["detail"]


@pytest.mark.asyncio
async def test_create_order_without_items_returns_422(client: AsyncClient) -> None:
    """POST /pedidos with empty items list must return 422."""
    payload = {**ORDER_PAYLOAD, "items": []}
    response = await client.post("/pedidos", json=payload)
    assert response.status_code == 422
