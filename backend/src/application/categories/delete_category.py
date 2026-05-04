from uuid import UUID

from src.core.exceptions import EntityNotFound
from src.domain.categories.repositories import AbstractCategoryRepository


class DeleteCategoryUseCase:
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self._categories = category_repo

    async def execute(self, category_id: UUID) -> None:
        category = await self._categories.get_by_id(category_id)
        if not category:
            raise EntityNotFound(f"Category {category_id} not found")
        await self._categories.delete(category_id)
