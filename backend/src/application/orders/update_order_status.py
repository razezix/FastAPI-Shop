from uuid import UUID

from src.core.exceptions import AccessDenied, EntityNotFound
from src.domain.orders.entities import Order
from src.domain.orders.enums import OrderStatus
from src.domain.orders.repositories import AbstractOrderRepository
from src.domain.users.enums import UserRole


class UpdateOrderStatusUseCase:
    def __init__(self, order_repo: AbstractOrderRepository) -> None:
        self._orders = order_repo

    async def execute(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        acting_user_id: UUID,
        acting_user_role: UserRole,
    ) -> Order:
        order = await self._orders.get_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order {order_id} not found")

        if acting_user_role == UserRole.USER:
            # Users can only cancel their own PENDING orders
            if order.user_id != acting_user_id:
                raise AccessDenied("You can only cancel your own orders")
            if new_status != OrderStatus.CANCELLED:
                raise AccessDenied("Users can only cancel orders")

        order.transition_to(new_status)
        return await self._orders.update(order)
