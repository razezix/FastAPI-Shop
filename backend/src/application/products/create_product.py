from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from src.core.exceptions import EntityNotFound
from src.domain.products.entities import Product
from src.domain.products.repositories import AbstractProductRepository
from src.domain.categories.repositories import AbstractCategoryRepository
from src.domain.services.cache_service import AbstractCacheService


@dataclass
class CreateProductInput:
    name: str
    description: str
    price: Decimal
    category_id: UUID
    stock_quantity: int
    image_urls: list[str]


class CreateProductUseCase:
    def __init__(
        self,
        product_repo: AbstractProductRepository,
        category_repo: AbstractCategoryRepository,
        cache: AbstractCacheService,
    ) -> None:
        self._products = product_repo
        self._categories = category_repo
        self._cache = cache

    async def execute(self, input: CreateProductInput) -> Product:
        category = await self._categories.get_by_id(input.category_id)
        if not category:
            raise EntityNotFound(f"Category {input.category_id} not found")

        now = datetime.now(timezone.utc)
        product = Product(
            id=uuid4(),
            name=input.name,
            description=input.description,
            price=input.price,
            category_id=input.category_id,
            stock_quantity=input.stock_quantity,
            is_archived=False,
            average_rating=Decimal("0.00"),
            review_count=0,
            view_count=0,
            purchase_count=0,
            images=input.image_urls,
            created_at=now,
            updated_at=now,
        )
        created = await self._products.create(product)
        await self._cache.invalidate_pattern("popular_this_week:*")
        return created
