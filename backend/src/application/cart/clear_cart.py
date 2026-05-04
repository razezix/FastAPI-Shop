from uuid import UUID

from src.domain.cart.entities import Cart
from src.domain.cart.repositories import AbstractCartRepository


class ClearCartUseCase:
    def __init__(self, cart_repo: AbstractCartRepository) -> None:
        self._carts = cart_repo

    async def execute(self, user_id: UUID) -> Cart:
        cart = await self._carts.get_or_create(user_id)
        await self._carts.clear(cart.id)
        return await self._carts.get_or_create(user_id)
