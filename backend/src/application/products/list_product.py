from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.domain.products.entities import Product
from src.domain.products.repositories import AbstractProductRepository


@dataclass
class ListProductsInput:
    query: str | None = None
    category_id: UUID | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    in_stock_only: bool = False
    page: int = 1
    page_size: int = 20


@dataclass
class PaginatedProducts:
    items: list[Product]
    total: int
    page: int
    page_size: int
    pages: int


class ListProductsUseCase:
    def __init__(self, product_repo: AbstractProductRepository) -> None:
        self._products = product_repo

    async def execute(self, input: ListProductsInput) -> PaginatedProducts:
        skip = (input.page - 1) * input.page_size
        items, total = await self._products.search(
            query=input.query,
            category_id=input.category_id,
            min_price=input.min_price,
            max_price=input.max_price,
            in_stock_only=input.in_stock_only,
            skip=skip,
            limit=input.page_size,
        )
        pages = max(1, (total + input.page_size - 1) // input.page_size)
        return PaginatedProducts(items=items, total=total, page=input.page, page_size=input.page_size, pages=pages)
