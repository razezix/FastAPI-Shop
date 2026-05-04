from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from src.domain.products.entities import Product


class AbstractProductRepository(ABC):
    @abstractmethod
    async def create(self, product: Product) -> Product: ...

    @abstractmethod
    async def get_by_id(self, product_id: UUID, include_archived: bool = False) -> Product | None: ...

    @abstractmethod
    async def update(self, product: Product) -> Product: ...

    @abstractmethod
    async def archive(self, product_id: UUID) -> Product: ...

    @abstractmethod
    async def restore(self, product_id: UUID) -> Product: ...

    @abstractmethod
    async def search(
        self,
        query: str | None,
        category_id: UUID | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        in_stock_only: bool,
        skip: int,
        limit: int,
    ) -> tuple[list[Product], int]: ...

    @abstractmethod
    async def increment_view_count(self, product_id: UUID) -> None: ...

    @abstractmethod
    async def increment_purchase_count(self, product_id: UUID, quantity: int) -> None: ...

    @abstractmethod
    async def update_rating(self, product_id: UUID, average: Decimal, count: int) -> None: ...

    @abstractmethod
    async def decrement_stock(self, product_id: UUID, quantity: int) -> None: ...
