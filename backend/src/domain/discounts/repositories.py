from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.discounts.entities import Discount


class AbstractDiscountRepository(ABC):
    @abstractmethod
    async def create(self, discount: Discount) -> Discount: ...

    @abstractmethod
    async def get_by_id(self, discount_id: UUID) -> Discount | None: ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Discount | None: ...

    @abstractmethod
    async def update(self, discount: Discount) -> Discount: ...

    @abstractmethod
    async def deactivate(self, discount_id: UUID) -> Discount: ...

    @abstractmethod
    async def increment_usage(self, discount_id: UUID) -> None: ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 20) -> tuple[list[Discount], int]: ...
