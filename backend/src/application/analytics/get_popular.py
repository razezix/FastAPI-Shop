import json

from src.domain.analytics.entities import WeeklyPopularProduct
from src.domain.analytics.repositories import AbstractAnalyticsRepository
from src.domain.services.cache_service import AbstractCacheService


class GetPopularThisWeekUseCase:
    def __init__(
        self,
        analytics_repo: AbstractAnalyticsRepository,
        cache: AbstractCacheService,
    ) -> None:
        self._analytics = analytics_repo
        self._cache = cache

    async def execute(self, limit: int = 10) -> list[WeeklyPopularProduct]:
        cache_key = f"popular_this_week:{limit}"
        cached = await self._cache.get(cache_key)
        if cached:
            try:
                data = json.loads(cached)
                return [
                    WeeklyPopularProduct(
                        product_id=__import__("uuid").UUID(d["product_id"]),
                        product_name=d["product_name"],
                        price=__import__("decimal").Decimal(str(d["price"])),
                        average_rating=__import__("decimal").Decimal(str(d["average_rating"])),
                        view_count=d["view_count"],
                        purchase_count=d["purchase_count"],
                        score=d["score"],
                        images=d["images"],
                    )
                    for d in data
                ]
            except Exception:
                pass

        results = await self._analytics.get_popular_this_week(limit)

        try:
            serializable = [
                {
                    "product_id": str(r.product_id),
                    "product_name": r.product_name,
                    "price": float(r.price),
                    "average_rating": float(r.average_rating),
                    "view_count": r.view_count,
                    "purchase_count": r.purchase_count,
                    "score": r.score,
                    "images": r.images,
                }
                for r in results
            ]
            await self._cache.set(cache_key, json.dumps(serializable), ttl_seconds=3600)
        except Exception:
            pass

        return results
