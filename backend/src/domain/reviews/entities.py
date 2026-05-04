from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.core.exceptions import InvalidRating


@dataclass
class Review:
    id: UUID
    product_id: UUID
    user_id: UUID
    rating: int
    title: str
    body: str
    is_verified_purchase: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not (1 <= self.rating <= 5):
            raise InvalidRating(f"Rating must be between 1 and 5, got {self.rating}")
