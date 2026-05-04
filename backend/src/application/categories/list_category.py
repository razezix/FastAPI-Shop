from src.domain.categories.entities import Category
from src.domain.categories.repositories import AbstractCategoryRepository


class ListCategoriesUseCase:
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self._categories = category_repo

    async def execute(self) -> list[Category]:
        return await self._categories.list_all()
