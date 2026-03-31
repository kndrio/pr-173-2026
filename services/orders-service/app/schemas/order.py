import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.models.order import OrderStatus, Priority


class OrderItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=Decimal("0"), decimal_places=2)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: EmailStr
    description: str = Field(min_length=1)
    items: list[OrderItemCreate] = Field(min_length=1)
    priority: Priority = Priority.media
    notes: str | None = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_name: str
    customer_email: str
    description: str
    priority: Priority
    status: OrderStatus
    notes: str | None
    total_amount: Decimal
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}


class OrderListItemResponse(BaseModel):
    """Summary view of an order (without items) for list endpoints."""

    id: uuid.UUID
    customer_name: str
    customer_email: str
    description: str
    priority: Priority
    status: OrderStatus
    total_amount: Decimal
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatusCount(BaseModel):
    status: OrderStatus
    count: int


class PriorityCount(BaseModel):
    priority: Priority
    count: int


class OrderFilters(BaseModel):
    status_counts: list[StatusCount] = []
    priority_counts: list[PriorityCount] = []


class OrderListResponse(BaseModel):
    items: list[OrderListItemResponse]
    total: int
    page: int
    page_size: int
    pages: int
    filters: OrderFilters


class AIAnalysisResponse(BaseModel):
    order_id: uuid.UUID
    suggested_priority: Priority
    executive_summary: str
    source: str  # "ai" or "fallback"
