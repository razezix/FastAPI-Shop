from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class WishlistItem:
    id: UUID
    user_id: UUID
    product_id: UUID
    added_at: datetime
