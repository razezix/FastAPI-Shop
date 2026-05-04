from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.wishlist.entities import WishlistItem
from src.domain.wishlist.repositories import AbstractWishlistRepository
from src.infrastructure.database.models.wishlist import WishlistItemModel


def _to_entity(m: WishlistItemModel) -> WishlistItem:
    return WishlistItem(
        id=UUID(m.id),
        user_id=UUID(m.user_id),
        product_id=UUID(m.product_id),
        added_at=m.added_at,
    )


class SQLAlchemyWishlistRepository(AbstractWishlistRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, item: WishlistItem) -> WishlistItem:
        model = WishlistItemModel(
            id=str(item.id),
            user_id=str(item.user_id),
            product_id=str(item.product_id),
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def remove(self, user_id: UUID, product_id: UUID) -> None:
        await self._session.execute(
            delete(WishlistItemModel).where(
                WishlistItemModel.user_id == str(user_id),
                WishlistItemModel.product_id == str(product_id),
            )
        )

    async def get(self, user_id: UUID, product_id: UUID) -> WishlistItem | None:
        result = await self._session.execute(
            select(WishlistItemModel).where(
                WishlistItemModel.user_id == str(user_id),
                WishlistItemModel.product_id == str(product_id),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def list_by_user(self, user_id: UUID) -> list[WishlistItem]:
        result = await self._session.execute(
            select(WishlistItemModel)
            .where(WishlistItemModel.user_id == str(user_id))
            .order_by(WishlistItemModel.added_at.desc())
        )
        return [_to_entity(m) for m in result.scalars()]
