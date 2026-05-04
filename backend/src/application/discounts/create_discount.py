from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.discounts.entities import Discount, DiscountType
from src.domain.discounts.repositories import AbstractDiscountRepository


@dataclass
class CreateDiscountInput:
    code: str
    discount_type: DiscountType
    value: Decimal
    created_by: UUID
    min_order_amount: Decimal | None = None
    max_discount_amount: Decimal | None = None
    usage_limit: int | None = None
    valid_until: datetime | None = None


class CreateDiscountUseCase:
    def __init__(self, discount_repo: AbstractDiscountRepository) -> None:
        self._discounts = discount_repo

    async def execute(self, input: CreateDiscountInput) -> Discount:
        now = datetime.now(timezone.utc)
        discount = Discount(
            id=uuid4(),
            code=input.code.upper(),
            discount_type=input.discount_type,
            value=input.value,
            min_order_amount=input.min_order_amount,
            max_discount_amount=input.max_discount_amount,
            usage_limit=input.usage_limit,
            used_count=0,
            is_active=True,
            valid_from=now,
            valid_until=input.valid_until,
            created_by=input.created_by,
            created_at=now,
        )
        return await self._discounts.create(discount)
