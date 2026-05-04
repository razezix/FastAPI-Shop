from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.categories.entities import Category
from src.domain.categories.repositories import AbstractCategoryRepository
from src.infrastructure.database.models.category import CategoryModel


def _to_entity(m: CategoryModel) -> Category:
    return Category(
        id=UUID(m.id),
        name=m.name,
        slug=m.slug,
        description=m.description,
        parent_id=UUID(m.parent_id) if m.parent_id else None,
        is_active=m.is_active,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SQLAlchemyCategoryRepository(AbstractCategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, category: Category) -> Category:
        model = CategoryModel(
            id=str(category.id),
            name=category.name,
            slug=category.slug,
            description=category.description,
            parent_id=str(category.parent_id) if category.parent_id else None,
            is_active=category.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, category_id: UUID) -> Category | None:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == str(category_id))
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update(self, category: Category) -> Category:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == str(category.id))
        )
        model = result.scalar_one()
        model.name = category.name
        model.slug = category.slug
        model.description = category.description
        model.parent_id = str(category.parent_id) if category.parent_id else None
        model.is_active = category.is_active
        await self._session.flush()
        return _to_entity(model)

    async def delete(self, category_id: UUID) -> None:
        await self._session.execute(
            delete(CategoryModel).where(CategoryModel.id == str(category_id))
        )

    async def list_all(self) -> list[Category]:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.is_active == True).order_by(CategoryModel.name)  # noqa: E712
        )
        return [_to_entity(m) for m in result.scalars()]

    async def list_children(self, parent_id: UUID) -> list[Category]:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.parent_id == str(parent_id))
        )
        return [_to_entity(m) for m in result.scalars()]
