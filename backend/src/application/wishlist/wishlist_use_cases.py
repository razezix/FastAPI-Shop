from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.core.exceptions import EntityNotFound
from src.domain.products.repositories import AbstractProductRepository
from src.domain.wishlist.entities import WishlistItem
from src.domain.wishlist.repositories import AbstractWishlistRepository


class AddToWishlistUseCase:
    def __init__(
        self,
        wishlist_repo: AbstractWishlistRepository,
        product_repo: AbstractProductRepository,
    ) -> None:
        self._wishlist = wishlist_repo
        self._products = product_repo

    async def execute(self, user_id: UUID, product_id: UUID) -> WishlistItem:
        product = await self._products.get_by_id(product_id)
        if not product:
            raise EntityNotFound(f"Product {product_id} not found")

        existing = await self._wishlist.get(user_id, product_id)
        if existing:
            return existing

        item = WishlistItem(
            id=uuid4(),
            user_id=user_id,
            product_id=product_id,
            added_at=datetime.now(timezone.utc),
        )
        return await self._wishlist.add(item)


class RemoveFromWishlistUseCase:
    def __init__(self, wishlist_repo: AbstractWishlistRepository) -> None:
        self._wishlist = wishlist_repo

    async def execute(self, user_id: UUID, product_id: UUID) -> None:
        await self._wishlist.remove(user_id, product_id)


class GetWishlistUseCase:
    def __init__(self, wishlist_repo: AbstractWishlistRepository) -> None:
        self._wishlist = wishlist_repo

    async def execute(self, user_id: UUID) -> list[WishlistItem]:
        return await self._wishlist.list_by_user(user_id)
