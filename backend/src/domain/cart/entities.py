from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class CartItem:
    id: UUID
    cart_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    added_at: datetime

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Cart:
    id: UUID
    user_id: UUID
    items: list[CartItem]
    created_at: datetime
    updated_at: datetime

    @property
    def total(self) -> Decimal:
        return sum(item.subtotal for item in self.items)

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0
