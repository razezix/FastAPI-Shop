from decimal import Decimal
from uuid import UUID

from src.core.exceptions import AccessDenied, EntityNotFound
from src.domain.products.repositories import AbstractProductRepository
from src.domain.reviews.repositories import AbstractReviewRepository
from src.domain.users.enums import UserRole


class DeleteReviewUseCase:
    def __init__(
        self,
        review_repo: AbstractReviewRepository,
        product_repo: AbstractProductRepository,
    ) -> None:
        self._reviews = review_repo
        self._products = product_repo

    async def execute(self, review_id: UUID, user_id: UUID, user_role: UserRole) -> None:
        review = await self._reviews.get_by_id(review_id)
        if not review:
            raise EntityNotFound(f"Review {review_id} not found")
        if review.user_id != user_id and user_role != UserRole.ADMIN:
            raise AccessDenied("You can only delete your own reviews")

        product_id = review.product_id
        await self._reviews.delete(review_id)

        avg, count = await self._reviews.calculate_product_rating(product_id)
        await self._products.update_rating(product_id, Decimal(str(round(avg, 2))), count)
