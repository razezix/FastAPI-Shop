from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.orders.entities import Order
from src.domain.orders.enums import OrderStatus


class AbstractOrderRepository(ABC):
    @abstractmethod
    async def create(self, order: Order) -> Order: ...

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None: ...

    @abstractmethod
    async def update(self, order: Order) -> Order: ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 20) -> tuple[list[Order], int]: ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 20, status: OrderStatus | None = None) -> tuple[list[Order], int]: ...
