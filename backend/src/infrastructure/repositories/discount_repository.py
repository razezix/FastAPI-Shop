from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.discounts.entities import Discount, DiscountType
from src.domain.discounts.repositories import AbstractDiscountRepository
from src.infrastructure.database.models.discount import DiscountModel


def _to_entity(m: DiscountModel) -> Discount:
    return Discount(
        id=UUID(m.id),
        code=m.code,
        discount_type=DiscountType(m.discount_type),
        value=m.value,
        min_order_amount=m.min_order_amount,
        max_discount_amount=m.max_discount_amount,
        usage_limit=m.usage_limit,
        used_count=m.used_count,
        is_active=m.is_active,
        valid_from=m.valid_from,
        valid_until=m.valid_until,
        created_by=UUID(m.created_by),
        created_at=m.created_at,
    )


class SQLAlchemyDiscountRepository(AbstractDiscountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, discount: Discount) -> Discount:
        model = DiscountModel(
            id=str(discount.id),
            code=discount.code.upper(),
            discount_type=discount.discount_type.value,
            value=discount.value,
            min_order_amount=discount.min_order_amount,
            max_discount_amount=discount.max_discount_amount,
            usage_limit=discount.usage_limit,
            used_count=0,
            is_active=True,
            valid_from=discount.valid_from,
            valid_until=discount.valid_until,
            created_by=str(discount.created_by),
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, discount_id: UUID) -> Discount | None:
        result = await self._session.execute(
            select(DiscountModel).where(DiscountModel.id == str(discount_id))
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_code(self, code: str) -> Discount | None:
        result = await self._session.execute(
            select(DiscountModel).where(DiscountModel.code == code.upper())
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update(self, discount: Discount) -> Discount:
        result = await self._session.execute(
            select(DiscountModel).where(DiscountModel.id == str(discount.id))
        )
        model = result.scalar_one()
        model.value = discount.value
        model.min_order_amount = discount.min_order_amount
        model.max_discount_amount = discount.max_discount_amount
        model.usage_limit = discount.usage_limit
        model.is_active = discount.is_active
        model.valid_until = discount.valid_until
        await self._session.flush()
        return _to_entity(model)

    async def deactivate(self, discount_id: UUID) -> Discount:
        await self._session.execute(
            update(DiscountModel).where(DiscountModel.id == str(discount_id)).values(is_active=False)
        )
        result = await self._session.execute(
            select(DiscountModel).where(DiscountModel.id == str(discount_id))
        )
        return _to_entity(result.scalar_one())

    async def increment_usage(self, discount_id: UUID) -> None:
        await self._session.execute(
            update(DiscountModel)
            .where(DiscountModel.id == str(discount_id))
            .values(used_count=DiscountModel.used_count + 1)
        )

    async def list_all(self, skip: int = 0, limit: int = 20) -> tuple[list[Discount], int]:
        count_result = await self._session.execute(select(func.count()).select_from(DiscountModel))
        total = count_result.scalar_one()
        result = await self._session.execute(
            select(DiscountModel).order_by(DiscountModel.created_at.desc()).offset(skip).limit(limit)
        )
        return [_to_entity(m) for m in result.scalars()], total
