from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import EntityNotFound, InsufficientStock
from src.domain.products.entities import Product
from src.domain.products.repositories import AbstractProductRepository
from src.infrastructure.database.models.product import ProductImageModel, ProductModel


def _to_entity(m: ProductModel) -> Product:
    return Product(
        id=UUID(m.id),
        name=m.name,
        description=m.description,
        price=m.price,
        category_id=UUID(m.category_id),
        stock_quantity=m.stock_quantity,
        is_archived=m.is_archived,
        average_rating=m.average_rating,
        review_count=m.review_count,
        view_count=m.view_count,
        purchase_count=m.purchase_count,
        images=[img.url for img in sorted(m.images, key=lambda i: i.display_order)],
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SQLAlchemyProductRepository(AbstractProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, product: Product) -> Product:
        model = ProductModel(
            id=str(product.id),
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=str(product.category_id),
            stock_quantity=product.stock_quantity,
            is_archived=False,
            average_rating=Decimal("0.00"),
            review_count=0,
            view_count=0,
            purchase_count=0,
        )
        self._session.add(model)
        await self._session.flush()
        for i, url in enumerate(product.images):
            img = ProductImageModel(product_id=str(product.id), url=url, display_order=i)
            self._session.add(img)
        await self._session.flush()
        return await self._load(str(product.id))

    async def get_by_id(self, product_id: UUID, include_archived: bool = False) -> Product | None:
        stmt = (
            select(ProductModel)
            .options(selectinload(ProductModel.images))
            .where(ProductModel.id == str(product_id))
        )
        if not include_archived:
            stmt = stmt.where(ProductModel.is_archived == False)  # noqa: E712
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update(self, product: Product) -> Product:
        await self._session.execute(
            update(ProductModel)
            .where(ProductModel.id == str(product.id))
            .values(
                name=product.name,
                description=product.description,
                price=product.price,
                category_id=str(product.category_id),
                stock_quantity=product.stock_quantity,
            )
        )
        existing_images = await self._session.execute(
            select(ProductImageModel).where(ProductImageModel.product_id == str(product.id))
        )
        for img in existing_images.scalars():
            await self._session.delete(img)
        for i, url in enumerate(product.images):
            self._session.add(ProductImageModel(product_id=str(product.id), url=url, display_order=i))
        await self._session.flush()
        return await self._load(str(product.id))

    async def archive(self, product_id: UUID) -> Product:
        await self._session.execute(
            update(ProductModel).where(ProductModel.id == str(product_id)).values(is_archived=True)
        )
        return await self._load(str(product_id))

    async def restore(self, product_id: UUID) -> Product:
        await self._session.execute(
            update(ProductModel).where(ProductModel.id == str(product_id)).values(is_archived=False)
        )
        return await self._load(str(product_id), include_archived=True)

    async def search(
        self,
        query: str | None,
        category_id: UUID | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        in_stock_only: bool,
        skip: int,
        limit: int,
    ) -> tuple[list[Product], int]:
        stmt = (
            select(ProductModel)
            .options(selectinload(ProductModel.images))
            .where(ProductModel.is_archived == False)  # noqa: E712
        )
        if query:
            stmt = stmt.where(ProductModel.name.ilike(f"%{query}%"))
        if category_id:
            stmt = stmt.where(ProductModel.category_id == str(category_id))
        if min_price is not None:
            stmt = stmt.where(ProductModel.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(ProductModel.price <= max_price)
        if in_stock_only:
            stmt = stmt.where(ProductModel.stock_quantity > 0)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        result = await self._session.execute(stmt.offset(skip).limit(limit))
        return [_to_entity(m) for m in result.scalars()], total

    async def increment_view_count(self, product_id: UUID) -> None:
        await self._session.execute(
            update(ProductModel)
            .where(ProductModel.id == str(product_id))
            .values(view_count=ProductModel.view_count + 1)
        )

    async def increment_purchase_count(self, product_id: UUID, quantity: int) -> None:
        await self._session.execute(
            update(ProductModel)
            .where(ProductModel.id == str(product_id))
            .values(purchase_count=ProductModel.purchase_count + quantity)
        )

    async def update_rating(self, product_id: UUID, average: Decimal, count: int) -> None:
        await self._session.execute(
            update(ProductModel)
            .where(ProductModel.id == str(product_id))
            .values(average_rating=average, review_count=count)
        )

    async def decrement_stock(self, product_id: UUID, quantity: int) -> None:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == str(product_id)).with_for_update()
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFound(f"Product {product_id} not found")
        if model.stock_quantity < quantity:
            raise InsufficientStock(f"Not enough stock for product {product_id}")
        await self._session.execute(
            update(ProductModel)
            .where(ProductModel.id == str(product_id))
            .values(stock_quantity=ProductModel.stock_quantity - quantity)
        )

    async def _load(self, product_id: str, include_archived: bool = False) -> Product:
        stmt = (
            select(ProductModel)
            .options(selectinload(ProductModel.images))
            .where(ProductModel.id == product_id)
        )
        if not include_archived:
            stmt = stmt.where(ProductModel.is_archived == False)  # noqa: E712
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            # Try again without archived filter
            result = await self._session.execute(
                select(ProductModel).options(selectinload(ProductModel.images)).where(ProductModel.id == product_id)
            )
            model = result.scalar_one()
        return _to_entity(model)
