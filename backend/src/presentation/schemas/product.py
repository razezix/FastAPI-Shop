from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    description: str = ""
    price: Decimal = Field(gt=0, decimal_places=2)
    category_id: UUID
    stock_quantity: int = Field(ge=0)
    image_urls: list[str] = Field(default_factory=list, max_length=10)


class ProductUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    price: Decimal | None = Field(None, gt=0)
    category_id: UUID | None = None
    stock_quantity: int | None = Field(None, ge=0)
    image_urls: list[str] | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    price: Decimal
    category_id: UUID
    stock_quantity: int
    is_archived: bool
    average_rating: Decimal
    review_count: int
    view_count: int
    purchase_count: int
    images: list[str]
    created_at: datetime


class PaginatedProductsResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PopularProductResponse(BaseModel):
    product_id: UUID
    product_name: str
    price: Decimal
    average_rating: Decimal
    view_count: int
    purchase_count: int
    score: float
    images: list[str]
