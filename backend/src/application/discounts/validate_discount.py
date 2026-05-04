from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from src.core.exceptions import (
    DiscountExpired,
    DiscountUsageLimitReached,
    InvalidDiscountCode,
)
from src.domain.discounts.entities import Discount
from src.domain.discounts.repositories import AbstractDiscountRepository


@dataclass
class ValidateDiscountOutput:
    discount: Discount
    discount_amount: Decimal


class ValidateDiscountUseCase:
    def __init__(self, discount_repo: AbstractDiscountRepository) -> None:
        self._discounts = discount_repo

    async def execute(self, code: str, order_amount: Decimal) -> ValidateDiscountOutput:
        discount = await self._discounts.get_by_code(code)
        if not discount or not discount.is_active:
            raise InvalidDiscountCode(f"Discount code '{code}' is invalid")

        now = datetime.now(timezone.utc)
        if discount.valid_until and discount.valid_until < now:
            raise DiscountExpired("Discount code has expired")
        if discount.valid_from > now:
            raise InvalidDiscountCode("Discount code is not yet valid")
        if discount.usage_limit is not None and discount.used_count >= discount.usage_limit:
            raise DiscountUsageLimitReached("Discount code usage limit reached")
        if discount.min_order_amount and order_amount < discount.min_order_amount:
            raise InvalidDiscountCode(
                f"Minimum order amount is ${discount.min_order_amount}"
            )

        return ValidateDiscountOutput(
            discount=discount,
            discount_amount=discount.calculate_discount(order_amount),
        )
