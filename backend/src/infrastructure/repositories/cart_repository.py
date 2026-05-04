from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.cart.entities import Cart, CartItem
from src.domain.cart.repositories import AbstractCartRepository
from src.infrastructure.database.models.cart import CartItemModel, CartModel


def _item_to_entity(m: CartItemModel) -> CartItem:
    return CartItem(
        id=UUID(m.id),
        cart_id=UUID(m.cart_id),
        product_id=UUID(m.product_id),
        quantity=m.quantity,
        unit_price=m.unit_price,
        added_at=m.added_at,
    )


def _to_entity(m: CartModel) -> Cart:
    return Cart(
        id=UUID(m.id),
        user_id=UUID(m.user_id),
        items=[_item_to_entity(i) for i in m.items],
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SQLAlchemyCartRepository(AbstractCartRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create(self, user_id: UUID) -> Cart:
        cart = await self.get_by_user_id(user_id)
        if cart:
            return cart
        model = CartModel(id=str(uuid4()), user_id=str(user_id))
        self._session.add(model)
        await self._session.flush()
        return await self._load(str(user_id))

    async def get_by_user_id(self, user_id: UUID) -> Cart | None:
        result = await self._session.execute(
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.user_id == str(user_id))
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def add_item(self, cart_id: UUID, item: CartItem) -> CartItem:
        # Check if item for same product already exists
        existing = await self._session.execute(
            select(CartItemModel).where(
                CartItemModel.cart_id == str(cart_id),
                CartItemModel.product_id == str(item.product_id),
            )
        )
        existing_model = existing.scalar_one_or_none()
        if existing_model:
            existing_model.quantity += item.quantity
            await self._session.flush()
            return _item_to_entity(existing_model)

        model = CartItemModel(
            id=str(item.id),
            cart_id=str(cart_id),
            product_id=str(item.product_id),
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        self._session.add(model)
        await self._session.flush()
        return _item_to_entity(model)

    async def get_item(self, item_id: UUID) -> CartItem | None:
        result = await self._session.execute(
            select(CartItemModel).where(CartItemModel.id == str(item_id))
        )
        model = result.scalar_one_or_none()
        return _item_to_entity(model) if model else None

    async def update_item_quantity(self, item_id: UUID, quantity: int) -> CartItem:
        await self._session.execute(
            update(CartItemModel).where(CartItemModel.id == str(item_id)).values(quantity=quantity)
        )
        result = await self._session.execute(
            select(CartItemModel).where(CartItemModel.id == str(item_id))
        )
        return _item_to_entity(result.scalar_one())

    async def remove_item(self, item_id: UUID) -> None:
        await self._session.execute(
            delete(CartItemModel).where(CartItemModel.id == str(item_id))
        )

    async def clear(self, cart_id: UUID) -> None:
        await self._session.execute(
            delete(CartItemModel).where(CartItemModel.cart_id == str(cart_id))
        )

    async def _load(self, user_id: str) -> Cart:
        result = await self._session.execute(
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.user_id == user_id)
        )
        return _to_entity(result.scalar_one())
