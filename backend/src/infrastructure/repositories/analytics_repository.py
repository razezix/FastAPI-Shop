from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.analytics.entities import ProductView, WeeklyPopularProduct
from src.domain.analytics.repositories import AbstractAnalyticsRepository
from src.infrastructure.database.models.analytics import ProductViewModel
from src.infrastructure.database.models.order import OrderItemModel, OrderModel
from src.infrastructure.database.models.product import ProductModel, ProductImageModel
from src.infrastructure.database.models.user import UserModel


class SQLAlchemyAnalyticsRepository(AbstractAnalyticsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_product_view(self, view: ProductView) -> None:
        model = ProductViewModel(
            id=str(view.id),
            product_id=str(view.product_id),
            user_id=str(view.user_id) if view.user_id else None,
            session_id=view.session_id,
        )
        self._session.add(model)
        await self._session.flush()

    async def get_popular_this_week(self, limit: int = 10) -> list[WeeklyPopularProduct]:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        view_counts = (
            select(
                ProductViewModel.product_id,
                func.count(ProductViewModel.id).label("view_count"),
            )
            .where(ProductViewModel.viewed_at >= week_ago)
            .group_by(ProductViewModel.product_id)
            .subquery()
        )

        purchase_counts = (
            select(
                OrderItemModel.product_id,
                func.sum(OrderItemModel.quantity).label("purchase_count"),
            )
            .join(OrderModel, OrderModel.id == OrderItemModel.order_id)
            .where(
                OrderModel.created_at >= week_ago,
                OrderModel.status.in_(["PAID", "SHIPPED", "DELIVERED"]),
            )
            .group_by(OrderItemModel.product_id)
            .subquery()
        )

        stmt = (
            select(
                ProductModel.id,
                ProductModel.name,
                ProductModel.price,
                ProductModel.average_rating,
                func.coalesce(view_counts.c.view_count, 0).label("view_count"),
                func.coalesce(purchase_counts.c.purchase_count, 0).label("purchase_count"),
                (
                    func.coalesce(view_counts.c.view_count, 0) * 0.3
                    + func.coalesce(purchase_counts.c.purchase_count, 0) * 0.7
                ).label("score"),
            )
            .outerjoin(view_counts, view_counts.c.product_id == ProductModel.id)
            .outerjoin(purchase_counts, purchase_counts.c.product_id == ProductModel.id)
            .where(ProductModel.is_archived == False)  # noqa: E712
            .order_by(text("score DESC"))
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        popular = []
        for row in rows:
            image_result = await self._session.execute(
                select(ProductImageModel.url)
                .where(ProductImageModel.product_id == row.id)
                .order_by(ProductImageModel.display_order)
                .limit(1)
            )
            images = [image_result.scalar()] if image_result.scalar() else []
            popular.append(
                WeeklyPopularProduct(
                    product_id=UUID(row.id),
                    product_name=row.name,
                    price=row.price,
                    average_rating=row.average_rating,
                    view_count=int(row.view_count),
                    purchase_count=int(row.purchase_count),
                    score=float(row.score),
                    images=images,
                )
            )
        return popular

    async def get_revenue_by_period(self, start: datetime, end: datetime) -> Decimal:
        result = await self._session.execute(
            select(func.coalesce(func.sum(OrderModel.total_amount), 0))
            .where(
                OrderModel.created_at >= start,
                OrderModel.created_at <= end,
                OrderModel.status.in_(["PAID", "SHIPPED", "DELIVERED"]),
            )
        )
        return result.scalar_one()

    async def get_top_products_by_revenue(self, start: datetime, end: datetime, limit: int) -> list[dict]:
        result = await self._session.execute(
            select(
                OrderItemModel.product_id,
                OrderItemModel.product_name,
                func.sum(OrderItemModel.subtotal).label("revenue"),
                func.sum(OrderItemModel.quantity).label("units_sold"),
            )
            .join(OrderModel, OrderModel.id == OrderItemModel.order_id)
            .where(
                OrderModel.created_at >= start,
                OrderModel.created_at <= end,
                OrderModel.status.in_(["PAID", "SHIPPED", "DELIVERED"]),
            )
            .group_by(OrderItemModel.product_id, OrderItemModel.product_name)
            .order_by(text("revenue DESC"))
            .limit(limit)
        )
        return [
            {"product_id": str(r.product_id), "product_name": r.product_name, "revenue": float(r.revenue), "units_sold": int(r.units_sold)}
            for r in result.all()
        ]

    async def get_new_user_count(self, start: datetime, end: datetime) -> int:
        result = await self._session.execute(
            select(func.count(UserModel.id)).where(
                UserModel.created_at >= start, UserModel.created_at <= end
            )
        )
        return result.scalar_one()

    async def get_order_conversion_rate(self, start: datetime, end: datetime) -> float:
        total_users = await self._session.execute(
            select(func.count(UserModel.id)).where(
                UserModel.created_at >= start, UserModel.created_at <= end
            )
        )
        users = total_users.scalar_one()
        if users == 0:
            return 0.0
        orders = await self._session.execute(
            select(func.count(func.distinct(OrderModel.user_id))).where(
                OrderModel.created_at >= start, OrderModel.created_at <= end
            )
        )
        buyers = orders.scalar_one()
        return round(buyers / users * 100, 2)
