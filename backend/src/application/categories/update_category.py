from dataclasses import dataclass
from uuid import UUID

from src.core.exceptions import EntityNotFound
from src.domain.categories.entities import Category
from src.domain.categories.repositories import AbstractCategoryRepository


@dataclass
class UpdateCategoryInput:
    category_id: UUID
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    parent_id: UUID | None = None
    is_active: bool | None = None


class UpdateCategoryUseCase:
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self._categories = category_repo

    async def execute(self, input: UpdateCategoryInput) -> Category:
        category = await self._categories.get_by_id(input.category_id)
        if not category:
            raise EntityNotFound(f"Category {input.category_id} not found")

        if input.name is not None:
            category.name = input.name
        if input.slug is not None:
            category.slug = input.slug
        if input.description is not None:
            category.description = input.description
        if input.parent_id is not None:
            category.parent_id = input.parent_id
        if input.is_active is not None:
            category.is_active = input.is_active

        return await self._categories.update(category)
