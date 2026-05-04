from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.core.exceptions import EntityNotFound, InsufficientStock, ProductIsArchived
from src.domain.cart.entities import Cart, CartItem
from src.domain.cart.repositories import AbstractCartRepository
from src.domain.products.repositories import AbstractProductRepository


@dataclass
class AddCartItemInput:
    user_id: UUID
    product_id: UUID
    quantity: int


class AddCartItemUseCase:
    def __init__(
        self,
        cart_repo: AbstractCartRepository,
        product_repo: AbstractProductRepository,
    ) -> None:
        self._carts = cart_repo
        self._products = product_repo

    async def execute(self, input: AddCartItemInput) -> Cart:
        product = await self._products.get_by_id(input.product_id)
        if not product:
            raise EntityNotFound(f"Product {input.product_id} not found")
        if product.is_archived:
            raise ProductIsArchived("Product is no longer available")
        if not product.can_fulfill(input.quantity):
            raise InsufficientStock(f"Only {product.stock_quantity} units available")

        cart = await self._carts.get_or_create(input.user_id)
        item = CartItem(
            id=uuid4(),
            cart_id=cart.id,
            product_id=input.product_id,
            quantity=input.quantity,
            unit_price=product.price,
            added_at=datetime.now(timezone.utc),
        )
        await self._carts.add_item(cart.id, item)
        return await self._carts.get_or_create(input.user_id)
