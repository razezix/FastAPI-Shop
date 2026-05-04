from dataclasses import dataclass
from datetime import date, datetime, timezone

from src.domain.analytics.repositories import AbstractAnalyticsRepository


@dataclass
class RevenueOutput:
    start_date: str
    end_date: str
    total_revenue: float
    top_products: list[dict]
    new_users: int
    conversion_rate: float


class GetAnalyticsUseCase:
    def __init__(self, analytics_repo: AbstractAnalyticsRepository) -> None:
        self._analytics = analytics_repo

    async def execute(self, start: date, end: date, top_n: int = 10) -> RevenueOutput:
        start_dt = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
        end_dt = datetime(end.year, end.month, end.day, 23, 59, 59, tzinfo=timezone.utc)

        revenue = await self._analytics.get_revenue_by_period(start_dt, end_dt)
        top_products = await self._analytics.get_top_products_by_revenue(start_dt, end_dt, top_n)
        new_users = await self._analytics.get_new_user_count(start_dt, end_dt)
        conversion = await self._analytics.get_order_conversion_rate(start_dt, end_dt)

        return RevenueOutput(
            start_date=str(start),
            end_date=str(end),
            total_revenue=float(revenue),
            top_products=top_products,
            new_users=new_users,
            conversion_rate=conversion,
        )
