from dataclasses import dataclass
from uuid import UUID

from src.domain.orders.entities import Order
from src.domain.orders.repositories import AbstractOrderRepository


@dataclass
class PaginatedOrders:
    items: list[Order]
    total: int
    page: int
    page_size: int
    pages: int


class ListMyOrdersUseCase:
    def __init__(self, order_repo: AbstractOrderRepository) -> None:
        self._orders = order_repo

    async def execute(self, user_id: UUID, page: int = 1, page_size: int = 20) -> PaginatedOrders:
        skip = (page - 1) * page_size
        items, total = await self._orders.list_by_user(user_id, skip=skip, limit=page_size)
        pages = max(1, (total + page_size - 1) // page_size)
        return PaginatedOrders(items=items, total=total, page=page, page_size=page_size, pages=pages)
