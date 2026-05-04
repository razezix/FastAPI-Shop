from uuid import UUID

from src.core.exceptions import AccessDenied, EntityNotFound
from src.domain.cart.entities import Cart
from src.domain.cart.repositories import AbstractCartRepository


class RemoveCartItemUseCase:
    def __init__(self, cart_repo: AbstractCartRepository) -> None:
        self._carts = cart_repo

    async def execute(self, user_id: UUID, item_id: UUID) -> Cart:
        item = await self._carts.get_item(item_id)
        if not item:
            raise EntityNotFound(f"Cart item {item_id} not found")

        cart = await self._carts.get_by_user_id(user_id)
        if not cart or cart.id != item.cart_id:
            raise AccessDenied("Cannot modify another user's cart")

        await self._carts.remove_item(item_id)
        return await self._carts.get_or_create(user_id)
