from uuid import UUID

from src.core.exceptions import EntityNotFound
from src.domain.products.entities import Product
from src.domain.products.repositories import AbstractProductRepository


class ArchiveProductUseCase:
    def __init__(self, product_repo: AbstractProductRepository) -> None:
        self._products = product_repo

    async def execute(self, product_id: UUID) -> Product:
        product = await self._products.get_by_id(product_id, include_archived=True)
        if not product:
            raise EntityNotFound(f"Product {product_id} not found")
        return await self._products.archive(product_id)


class RestoreProductUseCase:
    def __init__(self, product_repo: AbstractProductRepository) -> None:
        self._products = product_repo

    async def execute(self, product_id: UUID) -> Product:
        product = await self._products.get_by_id(product_id, include_archived=True)
        if not product:
            raise EntityNotFound(f"Product {product_id} not found")
        return await self._products.restore(product_id)
