from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src.application.products.create_product import CreateProductInput, CreateProductUseCase
from src.application.products.delete_product import ArchiveProductUseCase, RestoreProductUseCase
from src.application.products.get_product import GetProductUseCase
from src.application.products.list_product import ListProductsInput, ListProductsUseCase
from src.application.analytics.get_popular import GetPopularThisWeekUseCase
from src.core.exceptions import EntityNotFound
from src.presentation.api.deps import (
    CurrentUser,
    ManagerOrAbove,
    get_analytics_repo,
    get_cache_service,
    get_category_repo,
    get_product_repo,
)
from src.presentation.schemas.product import (
    PaginatedProductsResponse,
    PopularProductResponse,
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
)

router = APIRouter(prefix="/products", tags=["products"])


def _to_response(p) -> ProductResponse:
    return ProductResponse(
        id=p.id,
        name=p.name,
        description=p.description,
        price=p.price,
        category_id=p.category_id,
        stock_quantity=p.stock_quantity,
        is_archived=p.is_archived,
        average_rating=p.average_rating,
        review_count=p.review_count,
        view_count=p.view_count,
        purchase_count=p.purchase_count,
        images=p.images,
        created_at=p.created_at,
    )


@router.get("/popular", response_model=list[PopularProductResponse])
async def get_popular(
    limit: int = Query(default=10, ge=1, le=50),
    analytics_repo=Depends(get_analytics_repo),
    cache=Depends(get_cache_service),
):
    use_case = GetPopularThisWeekUseCase(analytics_repo, cache)
    results = await use_case.execute(limit)
    return [
        PopularProductResponse(
            product_id=r.product_id,
            product_name=r.product_name,
            price=r.price,
            average_rating=r.average_rating,
            view_count=r.view_count,
            purchase_count=r.purchase_count,
            score=r.score,
            images=r.images,
        )
        for r in results
    ]


@router.get("", response_model=PaginatedProductsResponse)
async def list_products(
    query: str | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    min_price: Decimal | None = Query(default=None),
    max_price: Decimal | None = Query(default=None),
    in_stock_only: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    product_repo=Depends(get_product_repo),
):
    use_case = ListProductsUseCase(product_repo)
    result = await use_case.execute(
        ListProductsInput(
            query=query,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
            page=page,
            page_size=page_size,
        )
    )
    return PaginatedProductsResponse(
        items=[_to_response(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    request: Request,
    product_repo=Depends(get_product_repo),
    analytics_repo=Depends(get_analytics_repo),
    current_user: CurrentUser | None = None,
):
    try:
        session_id = request.headers.get("X-Session-ID")
        use_case = GetProductUseCase(product_repo, analytics_repo)
        product = await use_case.execute(
            product_id,
            user_id=current_user.id if current_user else None,
            session_id=session_id,
        )
        return _to_response(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    body: ProductCreateRequest,
    _: ManagerOrAbove,
    product_repo=Depends(get_product_repo),
    category_repo=Depends(get_category_repo),
    cache=Depends(get_cache_service),
):
    try:
        use_case = CreateProductUseCase(product_repo, category_repo, cache)
        product = await use_case.execute(
            CreateProductInput(
                name=body.name,
                description=body.description,
                price=body.price,
                category_id=body.category_id,
                stock_quantity=body.stock_quantity,
                image_urls=body.image_urls,
            )
        )
        return _to_response(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    body: ProductUpdateRequest,
    _: ManagerOrAbove,
    product_repo=Depends(get_product_repo),
    category_repo=Depends(get_category_repo),
):
    from src.application.products.update_product import UpdateProductInput, UpdateProductUseCase
    try:
        use_case = UpdateProductUseCase(product_repo, category_repo)
        product = await use_case.execute(
            UpdateProductInput(
                product_id=product_id,
                name=body.name,
                description=body.description,
                price=body.price,
                category_id=body.category_id,
                stock_quantity=body.stock_quantity,
                image_urls=body.image_urls,
            )
        )
        return _to_response(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{product_id}", response_model=ProductResponse)
async def archive_product(
    product_id: UUID,
    _: ManagerOrAbove,
    product_repo=Depends(get_product_repo),
):
    try:
        use_case = ArchiveProductUseCase(product_repo)
        return _to_response(await use_case.execute(product_id))
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{product_id}/restore", response_model=ProductResponse)
async def restore_product(
    product_id: UUID,
    _: ManagerOrAbove,
    product_repo=Depends(get_product_repo),
):
    try:
        use_case = RestoreProductUseCase(product_repo)
        return _to_response(await use_case.execute(product_id))
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
