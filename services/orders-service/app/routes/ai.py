import json
import uuid
from datetime import datetime, timezone

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import UserPayload, get_current_user
from app.models import Order
from app.schemas import AIAnalysisResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/pedidos", tags=["ai"])

_PRIORITY_LEVELS = ["baixa", "media", "alta", "urgente"]


def _rule_based_analysis(order: Order) -> AIAnalysisResponse:
    total = float(order.total_amount)
    item_count = len(order.items) if isinstance(order.items, list) else 0

    if total > 10000:
        priority = "urgente"
    elif total > 5000:
        priority = "alta"
    else:
        priority = "media"

    # Bump one level if order has many items
    if item_count > 3 and priority != "urgente":
        idx = _PRIORITY_LEVELS.index(priority)
        priority = _PRIORITY_LEVELS[min(idx + 1, 3)]

    return AIAnalysisResponse(
        suggested_priority=priority,
        executive_summary=(
            f"Pedido de {order.customer_name} com {item_count} item(s) "
            f"no valor de R$ {total:,.2f}. Status atual: {order.status.value}."
        ),
        observations=[
            f"Valor total: R$ {total:,.2f}",
            f"Número de itens: {item_count}",
            f"Prioridade atual: {order.priority.value}",
        ],
        model_used="rule-based-fallback",
        analyzed_at=datetime.now(timezone.utc),
    )


@router.post("/{order_id}/ai-analysis", response_model=AIAnalysisResponse)
async def ai_analysis(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: UserPayload = Depends(get_current_user),
) -> AIAnalysisResponse:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    logger.info("ai_analysis_requested", order_id=str(order_id))

    if not settings.anthropic_api_key:
        logger.info("ai_analysis_fallback", reason="no_api_key", order_id=str(order_id))
        return _rule_based_analysis(order)

    # NOTE: Production deployments should add per-user rate limiting here
    # (e.g. fastapi-limiter backed by Redis) to prevent unbounded Anthropic spend.

    try:
        # customer_email and created_by intentionally excluded — data minimisation
        order_data = {
            "id": str(order.id),
            "customer_name": order.customer_name,
            "description": order.description,
            "total_amount": str(order.total_amount),
            "status": order.status.value,
            "priority": order.priority.value,
            "items": order.items,
            "notes": order.notes,
        }

        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": (
                        "Você é um analista de pedidos governamentais. Analise os dados "
                        "do pedido e retorne APENAS um JSON com: suggested_priority "
                        "(baixa/media/alta/urgente), executive_summary (resumo executivo "
                        "em português, max 3 frases), observations (lista de até 3 "
                        "observações relevantes)."
                    ),
                    "messages": [
                        {"role": "user", "content": json.dumps(order_data, ensure_ascii=False)}
                    ],
                },
            )
        resp.raise_for_status()
        content = resp.json()["content"][0]["text"]
        parsed = json.loads(content)
        return AIAnalysisResponse(
            suggested_priority=parsed["suggested_priority"],
            executive_summary=parsed["executive_summary"],
            observations=parsed["observations"],
            model_used="claude-sonnet-4-20250514",
            analyzed_at=datetime.now(timezone.utc),
        )
    except httpx.HTTPError:
        logger.warning("ai_analysis_fallback", reason="http_error", order_id=str(order_id))
        return _rule_based_analysis(order)
    except (json.JSONDecodeError, KeyError):
        logger.warning("ai_analysis_fallback", reason="parse_error", order_id=str(order_id))
        return _rule_based_analysis(order)
    except Exception:
        logger.warning("ai_analysis_fallback", reason="unexpected_error", order_id=str(order_id))
        return _rule_based_analysis(order)
