from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class DiscountType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"


@dataclass
class Discount:
    id: UUID
    code: str
    discount_type: DiscountType
    value: Decimal
    min_order_amount: Decimal | None
    max_discount_amount: Decimal | None
    usage_limit: int | None
    used_count: int
    is_active: bool
    valid_from: datetime
    valid_until: datetime | None
    created_by: UUID
    created_at: datetime

    def calculate_discount(self, order_amount: Decimal) -> Decimal:
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = order_amount * (self.value / Decimal("100"))
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        return min(self.value, order_amount)
