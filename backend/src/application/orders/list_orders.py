from dataclasses import dataclass

from src.domain.orders.entities import Order
from src.domain.orders.enums import OrderStatus
from src.domain.orders.repositories import AbstractOrderRepository


@dataclass
class PaginatedOrders:
    items: list[Order]
    total: int
    page: int
    page_size: int
    pages: int


class ListOrdersUseCase:
    def __init__(self, order_repo: AbstractOrderRepository) -> None:
        self._orders = order_repo

    async def execute(
        self,
        page: int = 1,
        page_size: int = 20,
        status: OrderStatus | None = None,
    ) -> PaginatedOrders:
        skip = (page - 1) * page_size
        items, total = await self._orders.list_all(skip=skip, limit=page_size, status=status)
        pages = max(1, (total + page_size - 1) // page_size)
        return PaginatedOrders(items=items, total=total, page=page, page_size=page_size, pages=pages)
