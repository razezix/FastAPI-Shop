from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.core.exceptions import EntityNotFound
from src.domain.products.entities import Product
from src.domain.products.repositories import AbstractProductRepository
from src.domain.categories.repositories import AbstractCategoryRepository


@dataclass
class UpdateProductInput:
    product_id: UUID
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category_id: UUID | None = None
    stock_quantity: int | None = None
    image_urls: list[str] | None = None


class UpdateProductUseCase:
    def __init__(
        self,
        product_repo: AbstractProductRepository,
        category_repo: AbstractCategoryRepository,
    ) -> None:
        self._products = product_repo
        self._categories = category_repo

    async def execute(self, input: UpdateProductInput) -> Product:
        product = await self._products.get_by_id(input.product_id, include_archived=True)
        if not product:
            raise EntityNotFound(f"Product {input.product_id} not found")

        if input.category_id and input.category_id != product.category_id:
            category = await self._categories.get_by_id(input.category_id)
            if not category:
                raise EntityNotFound(f"Category {input.category_id} not found")
            product.category_id = input.category_id

        if input.name is not None:
            product.name = input.name
        if input.description is not None:
            product.description = input.description
        if input.price is not None:
            product.price = input.price
        if input.stock_quantity is not None:
            product.stock_quantity = input.stock_quantity
        if input.image_urls is not None:
            product.images = input.image_urls

        return await self._products.update(product)
