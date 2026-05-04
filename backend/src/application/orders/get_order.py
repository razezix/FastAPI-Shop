from uuid import UUID

from src.core.exceptions import AccessDenied, EntityNotFound
from src.domain.orders.entities import Order
from src.domain.orders.repositories import AbstractOrderRepository
from src.domain.users.enums import UserRole


class GetOrderUseCase:
    def __init__(self, order_repo: AbstractOrderRepository) -> None:
        self._orders = order_repo

    async def execute(self, order_id: UUID, user_id: UUID, user_role: UserRole) -> Order:
        order = await self._orders.get_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order {order_id} not found")
        if order.user_id != user_id and user_role == UserRole.USER:
            raise AccessDenied("You can only view your own orders")
        return order
