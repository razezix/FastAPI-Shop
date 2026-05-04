from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.categories.entities import Category


class AbstractCategoryRepository(ABC):
    @abstractmethod
    async def create(self, category: Category) -> Category: ...

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Category | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Category | None: ...

    @abstractmethod
    async def update(self, category: Category) -> Category: ...

    @abstractmethod
    async def delete(self, category_id: UUID) -> None: ...

    @abstractmethod
    async def list_all(self) -> list[Category]: ...

    @abstractmethod
    async def list_children(self, parent_id: UUID) -> list[Category]: ...
