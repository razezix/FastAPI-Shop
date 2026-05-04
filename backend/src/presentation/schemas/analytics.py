from datetime import date
from uuid import UUID

from pydantic import BaseModel


class AnalyticsRequest(BaseModel):
    start_date: date
    end_date: date


class AnalyticsResponse(BaseModel):
    start_date: str
    end_date: str
    total_revenue: float
    top_products: list[dict]
    new_users: int
    conversion_rate: float


class PopularProductResponse(BaseModel):
    product_id: UUID
    product_name: str
    price: float
    average_rating: float
    view_count: int
    purchase_count: int
    score: float
    images: list[str]
