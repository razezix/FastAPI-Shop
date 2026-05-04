from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.orders.entities import Order, OrderItem
from src.domain.orders.enums import OrderStatus
from src.domain.orders.repositories import AbstractOrderRepository
from src.infrastructure.database.models.order import OrderItemModel, OrderModel


def _item_to_entity(m: OrderItemModel) -> OrderItem:
    return OrderItem(
        id=UUID(m.id),
        order_id=UUID(m.order_id),
        product_id=UUID(m.product_id),
        product_name=m.product_name,
        quantity=m.quantity,
        unit_price=m.unit_price,
    )


def _to_entity(m: OrderModel) -> Order:
    return Order(
        id=UUID(m.id),
        user_id=UUID(m.user_id),
        status=OrderStatus(m.status),
        items=[_item_to_entity(i) for i in m.items],
        subtotal=m.subtotal,
        discount_amount=m.discount_amount,
        total_amount=m.total_amount,
        discount_id=UUID(m.discount_id) if m.discount_id else None,
        shipping_address=m.shipping_address,
        notes=m.notes,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SQLAlchemyOrderRepository(AbstractOrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, order: Order) -> Order:
        model = OrderModel(
            id=str(order.id),
            user_id=str(order.user_id),
            status=order.status.value,
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            discount_id=str(order.discount_id) if order.discount_id else None,
            shipping_address=order.shipping_address,
            notes=order.notes,
        )
        self._session.add(model)
        await self._session.flush()
        for item in order.items:
            item_model = OrderItemModel(
                id=str(item.id),
                order_id=str(order.id),
                product_id=str(item.product_id),
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            self._session.add(item_model)
        await self._session.flush()
        return await self._load(str(order.id))

    async def get_by_id(self, order_id: UUID) -> Order | None:
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == str(order_id))
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update(self, order: Order) -> Order:
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.id == str(order.id))
        )
        model = result.scalar_one()
        model.status = order.status.value
        await self._session.flush()
        return await self._load(str(order.id))

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 20) -> tuple[list[Order], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(OrderModel).where(OrderModel.user_id == str(user_id))
        )
        total = count_result.scalar_one()
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.user_id == str(user_id))
            .order_by(OrderModel.created_at.desc())
            .offset(skip).limit(limit)
        )
        return [_to_entity(m) for m in result.scalars()], total

    async def list_all(self, skip: int = 0, limit: int = 20, status: OrderStatus | None = None) -> tuple[list[Order], int]:
        stmt = select(OrderModel)
        if status:
            stmt = stmt.where(OrderModel.status == status.value)
        count_result = await self._session.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar_one()
        result = await self._session.execute(
            stmt.options(selectinload(OrderModel.items))
            .order_by(OrderModel.created_at.desc())
            .offset(skip).limit(limit)
        )
        return [_to_entity(m) for m in result.scalars()], total

    async def _load(self, order_id: str) -> Order:
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order_id)
        )
        return _to_entity(result.scalar_one())
