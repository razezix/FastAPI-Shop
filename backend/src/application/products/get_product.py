from uuid import UUID

from src.core.exceptions import EntityNotFound
from src.domain.analytics.entities import ProductView
from src.domain.analytics.repositories import AbstractAnalyticsRepository
from src.domain.products.entities import Product
from src.domain.products.repositories import AbstractProductRepository


class GetProductUseCase:
    def __init__(
        self,
        product_repo: AbstractProductRepository,
        analytics_repo: AbstractAnalyticsRepository,
    ) -> None:
        self._products = product_repo
        self._analytics = analytics_repo

    async def execute(
        self,
        product_id: UUID,
        user_id: UUID | None = None,
        session_id: str | None = None,
    ) -> Product:
        product = await self._products.get_by_id(product_id)
        if not product:
            raise EntityNotFound(f"Product {product_id} not found")

        from uuid import uuid4
        from datetime import datetime, timezone

        await self._products.increment_view_count(product_id)
        await self._analytics.record_product_view(
            ProductView(
                id=uuid4(),
                product_id=product_id,
                user_id=user_id,
                session_id=session_id,
                viewed_at=datetime.now(timezone.utc),
            )
        )
        product.view_count += 1
        return product
