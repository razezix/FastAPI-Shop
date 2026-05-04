from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from src.domain.analytics.entities import ProductView, WeeklyPopularProduct


class AbstractAnalyticsRepository(ABC):
    @abstractmethod
    async def record_product_view(self, view: ProductView) -> None: ...

    @abstractmethod
    async def get_popular_this_week(self, limit: int = 10) -> list[WeeklyPopularProduct]: ...

    @abstractmethod
    async def get_revenue_by_period(self, start: datetime, end: datetime) -> Decimal: ...

    @abstractmethod
    async def get_top_products_by_revenue(self, start: datetime, end: datetime, limit: int) -> list[dict]: ...

    @abstractmethod
    async def get_new_user_count(self, start: datetime, end: datetime) -> int: ...

    @abstractmethod
    async def get_order_conversion_rate(self, start: datetime, end: datetime) -> float: ...
