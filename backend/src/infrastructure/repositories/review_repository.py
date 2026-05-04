from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.reviews.entities import Review
from src.domain.reviews.repositories import AbstractReviewRepository
from src.infrastructure.database.models.review import ReviewModel


def _to_entity(m: ReviewModel) -> Review:
    return Review(
        id=UUID(m.id),
        product_id=UUID(m.product_id),
        user_id=UUID(m.user_id),
        rating=m.rating,
        title=m.title,
        body=m.body,
        is_verified_purchase=m.is_verified_purchase,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SQLAlchemyReviewRepository(AbstractReviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, review: Review) -> Review:
        model = ReviewModel(
            id=str(review.id),
            product_id=str(review.product_id),
            user_id=str(review.user_id),
            rating=review.rating,
            title=review.title,
            body=review.body,
            is_verified_purchase=review.is_verified_purchase,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, review_id: UUID) -> Review | None:
        result = await self._session.execute(
            select(ReviewModel).where(ReviewModel.id == str(review_id))
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_user_and_product(self, user_id: UUID, product_id: UUID) -> Review | None:
        result = await self._session.execute(
            select(ReviewModel).where(
                ReviewModel.user_id == str(user_id),
                ReviewModel.product_id == str(product_id),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update(self, review: Review) -> Review:
        result = await self._session.execute(
            select(ReviewModel).where(ReviewModel.id == str(review.id))
        )
        model = result.scalar_one()
        model.rating = review.rating
        model.title = review.title
        model.body = review.body
        await self._session.flush()
        return _to_entity(model)

    async def delete(self, review_id: UUID) -> None:
        result = await self._session.execute(
            select(ReviewModel).where(ReviewModel.id == str(review_id))
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_product(self, product_id: UUID, skip: int = 0, limit: int = 20) -> tuple[list[Review], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(ReviewModel).where(ReviewModel.product_id == str(product_id))
        )
        total = count_result.scalar_one()
        result = await self._session.execute(
            select(ReviewModel)
            .where(ReviewModel.product_id == str(product_id))
            .order_by(ReviewModel.created_at.desc())
            .offset(skip).limit(limit)
        )
        return [_to_entity(m) for m in result.scalars()], total

    async def calculate_product_rating(self, product_id: UUID) -> tuple[float, int]:
        result = await self._session.execute(
            select(func.avg(ReviewModel.rating), func.count(ReviewModel.id))
            .where(ReviewModel.product_id == str(product_id))
        )
        avg, count = result.one()
        return float(avg or 0), count or 0
