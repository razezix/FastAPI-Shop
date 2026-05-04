from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WishlistItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    added_at: datetime


class WishlistResponse(BaseModel):
    items: list[WishlistItemResponse]
    total: int
