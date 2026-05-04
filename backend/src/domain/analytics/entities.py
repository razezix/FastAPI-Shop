from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class ProductView:
    id: UUID
    product_id: UUID
    user_id: UUID | None
    session_id: str | None
    viewed_at: datetime


@dataclass
class WeeklyPopularProduct:
    product_id: UUID
    product_name: str
    price: Decimal
    average_rating: Decimal
    view_count: int
    purchase_count: int
    score: float
    images: list[str]
