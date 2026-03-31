import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, computed_field, model_validator

from app.models import OrderStatus, Priority


class OrderItem(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(gt=Decimal("0"), decimal_places=2)

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: EmailStr
    description: str = Field(min_length=1)
    items: list[OrderItem] = Field(min_length=1)
    priority: Priority = Priority.media
    notes: str | None = None

    @computed_field  # type: ignore[misc]
    @property
    def total_amount(self) -> Decimal:
        """Computed server-side — never accepted from client."""
        return sum(
            (item.quantity * item.unit_price for item in self.items),
            Decimal("0"),
        ).quantize(Decimal("0.01"))


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    priority: Priority | None = None
    notes: str | None = None


class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_name: str
    customer_email: str
    description: str
    items: list[OrderItem]
    total_amount: Decimal
    status: OrderStatus
    priority: Priority
    notes: str | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def coerce_items_from_json(cls, data: object) -> object:
        """
        Explicitly coerce items stored as list[dict] in the JSON column
        into list[OrderItem].  This is necessary because `from_attributes`
        alone does not convert nested dicts to nested models.
        """
        if hasattr(data, "__dict__"):
            # SQLAlchemy ORM object — items is a list of raw dicts
            raw: object = getattr(data, "items", None)
            if isinstance(raw, list) and raw and isinstance(raw[0], dict):
                object.__setattr__(
                    data,
                    "items",
                    [OrderItem(**item) for item in raw],
                )
        return data


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total_count: int
    page: int
    page_size: int
