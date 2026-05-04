from dataclasses import dataclass
from uuid import UUID

from src.core.exceptions import AccessDenied, EntityNotFound
from src.domain.cart.entities import Cart
from src.domain.cart.repositories import AbstractCartRepository


@dataclass
class UpdateCartItemInput:
    user_id: UUID
    item_id: UUID
    quantity: int


class UpdateCartItemUseCase:
    def __init__(self, cart_repo: AbstractCartRepository) -> None:
        self._carts = cart_repo

    async def execute(self, input: UpdateCartItemInput) -> Cart:
        item = await self._carts.get_item(input.item_id)
        if not item:
            raise EntityNotFound(f"Cart item {input.item_id} not found")

        cart = await self._carts.get_by_user_id(input.user_id)
        if not cart or cart.id != item.cart_id:
            raise AccessDenied("Cannot modify another user's cart")

        if input.quantity <= 0:
            await self._carts.remove_item(input.item_id)
        else:
            await self._carts.update_item_quantity(input.item_id, input.quantity)

        return await self._carts.get_or_create(input.user_id)
