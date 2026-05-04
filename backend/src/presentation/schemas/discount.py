from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.discounts.entities import DiscountType


class CreateDiscountRequest(BaseModel):
    code: str = Field(min_length=3, max_length=50)
    discount_type: DiscountType
    value: Decimal = Field(gt=0)
    min_order_amount: Decimal | None = Field(None, ge=0)
    max_discount_amount: Decimal | None = Field(None, ge=0)
    usage_limit: int | None = Field(None, ge=1)
    valid_until: datetime | None = None


class ValidateDiscountRequest(BaseModel):
    code: str
    order_amount: Decimal = Field(gt=0)


class DiscountResponse(BaseModel):
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


class ValidateDiscountResponse(BaseModel):
    discount: DiscountResponse
    discount_amount: Decimal


class PaginatedDiscountsResponse(BaseModel):
    items: list[DiscountResponse]
    total: int
    page: int
    page_size: int
    pages: int
