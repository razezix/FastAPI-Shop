from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.core.exceptions import DuplicateReview, EntityNotFound
from src.domain.orders.enums import OrderStatus
from src.domain.orders.repositories import AbstractOrderRepository
from src.domain.products.repositories import AbstractProductRepository
from src.domain.reviews.entities import Review
from src.domain.reviews.repositories import AbstractReviewRepository
from decimal import Decimal


@dataclass
class CreateReviewInput:
    user_id: UUID
    product_id: UUID
    rating: int
    title: str
    body: str


class CreateReviewUseCase:
    def __init__(
        self,
        review_repo: AbstractReviewRepository,
        product_repo: AbstractProductRepository,
        order_repo: AbstractOrderRepository,
    ) -> None:
        self._reviews = review_repo
        self._products = product_repo
        self._orders = order_repo

    async def execute(self, input: CreateReviewInput) -> Review:
        product = await self._products.get_by_id(input.product_id)
        if not product:
            raise EntityNotFound(f"Product {input.product_id} not found")

        existing = await self._reviews.get_by_user_and_product(input.user_id, input.product_id)
        if existing:
            raise DuplicateReview("You have already reviewed this product")

        # Check if verified purchase
        orders, _ = await self._orders.list_by_user(input.user_id, skip=0, limit=1000)
        is_verified = any(
            any(item.product_id == input.product_id for item in o.items)
            and o.status in (OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED)
            for o in orders
        )

        now = datetime.now(timezone.utc)
        review = Review(
            id=uuid4(),
            product_id=input.product_id,
            user_id=input.user_id,
            rating=input.rating,
            title=input.title,
            body=input.body,
            is_verified_purchase=is_verified,
            created_at=now,
            updated_at=now,
        )
        created = await self._reviews.create(review)

        avg, count = await self._reviews.calculate_product_rating(input.product_id)
        await self._products.update_rating(input.product_id, Decimal(str(round(avg, 2))), count)

        return created
