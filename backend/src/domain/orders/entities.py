from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.orders.enums import OrderStatus, VALID_TRANSITIONS
from src.core.exceptions import InvalidOrderStatusTransition


@dataclass
class OrderItem:
    id: UUID
    order_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    id: UUID
    user_id: UUID
    status: OrderStatus
    items: list[OrderItem]
    subtotal: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    discount_id: UUID | None
    shipping_address: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    def transition_to(self, new_status: OrderStatus) -> None:
        allowed = VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise InvalidOrderStatusTransition(
                f"Cannot transition order from {self.status} to {new_status}"
            )
        self.status = new_status
