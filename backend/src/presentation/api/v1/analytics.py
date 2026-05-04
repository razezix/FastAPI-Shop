from datetime import date

from fastapi import APIRouter, Depends, Query

from src.application.analytics.get_popular import GetPopularThisWeekUseCase
from src.application.analytics.get_revenue import GetAnalyticsUseCase
from src.presentation.api.deps import AdminOnly, get_analytics_repo, get_cache_service
from src.presentation.schemas.analytics import AnalyticsResponse, PopularProductResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/revenue", response_model=AnalyticsResponse)
async def get_revenue(
    _: AdminOnly,
    start_date: date = Query(...),
    end_date: date = Query(...),
    top_n: int = Query(default=10, ge=1, le=50),
    analytics_repo=Depends(get_analytics_repo),
):
    use_case = GetAnalyticsUseCase(analytics_repo)
    result = await use_case.execute(start_date, end_date, top_n)
    return AnalyticsResponse(
        start_date=result.start_date,
        end_date=result.end_date,
        total_revenue=result.total_revenue,
        top_products=result.top_products,
        new_users=result.new_users,
        conversion_rate=result.conversion_rate,
    )


@router.get("/popular", response_model=list[PopularProductResponse])
async def get_popular(
    _: AdminOnly,
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
            price=float(r.price),
            average_rating=float(r.average_rating),
            view_count=r.view_count,
            purchase_count=r.purchase_count,
            score=r.score,
            images=r.images,
        )
        for r in results
    ]
