from dataclasses import dataclass
from uuid import UUID

from src.domain.reviews.entities import Review
from src.domain.reviews.repositories import AbstractReviewRepository


@dataclass
class PaginatedReviews:
    items: list[Review]
    total: int
    page: int
    page_size: int
    pages: int


class ListReviewsUseCase:
    def __init__(self, review_repo: AbstractReviewRepository) -> None:
        self._reviews = review_repo

    async def execute(self, product_id: UUID, page: int = 1, page_size: int = 20) -> PaginatedReviews:
        skip = (page - 1) * page_size
        items, total = await self._reviews.list_by_product(product_id, skip=skip, limit=page_size)
        pages = max(1, (total + page_size - 1) // page_size)
        return PaginatedReviews(items=items, total=total, page=page, page_size=page_size, pages=pages)
