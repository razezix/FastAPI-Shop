from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.reviews.entities import Review


class AbstractReviewRepository(ABC):
    @abstractmethod
    async def create(self, review: Review) -> Review: ...

    @abstractmethod
    async def get_by_id(self, review_id: UUID) -> Review | None: ...

    @abstractmethod
    async def get_by_user_and_product(self, user_id: UUID, product_id: UUID) -> Review | None: ...

    @abstractmethod
    async def update(self, review: Review) -> Review: ...

    @abstractmethod
    async def delete(self, review_id: UUID) -> None: ...

    @abstractmethod
    async def list_by_product(self, product_id: UUID, skip: int = 0, limit: int = 20) -> tuple[list[Review], int]: ...

    @abstractmethod
    async def calculate_product_rating(self, product_id: UUID) -> tuple[float, int]: ...
