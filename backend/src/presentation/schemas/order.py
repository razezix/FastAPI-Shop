from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.orders.enums import OrderStatus


class PlaceOrderRequest(BaseModel):
    shipping_address: str
    discount_code: str | None = None
    notes: str | None = None


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    status: OrderStatus
    items: list[OrderItemResponse]
    subtotal: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    shipping_address: str
    notes: str | None
    created_at: datetime


class PaginatedOrdersResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int
    pages: int
