from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.core.exceptions import EntityNotFound
from src.domain.categories.entities import Category
from src.domain.categories.repositories import AbstractCategoryRepository


@dataclass
class CreateCategoryInput:
    name: str
    slug: str
    description: str | None = None
    parent_id: UUID | None = None


class CreateCategoryUseCase:
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self._categories = category_repo

    async def execute(self, input: CreateCategoryInput) -> Category:
        if input.parent_id:
            parent = await self._categories.get_by_id(input.parent_id)
            if not parent:
                raise EntityNotFound(f"Parent category {input.parent_id} not found")

        now = datetime.now(timezone.utc)
        category = Category(
            id=uuid4(),
            name=input.name,
            slug=input.slug,
            description=input.description,
            parent_id=input.parent_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        return await self._categories.create(category)
