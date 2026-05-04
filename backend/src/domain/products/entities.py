from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class ProductImage:
    id: UUID
    product_id: UUID
    url: str
    display_order: int
    created_at: datetime


@dataclass
class Product:
    id: UUID
    name: str
    description: str
    price: Decimal
    category_id: UUID
    stock_quantity: int
    is_archived: bool
    average_rating: Decimal
    review_count: int
    view_count: int
    purchase_count: int
    images: list[str]
    created_at: datetime
    updated_at: datetime

    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0 and not self.is_archived

    def can_fulfill(self, quantity: int) -> bool:
        return self.stock_quantity >= quantity and not self.is_archived
