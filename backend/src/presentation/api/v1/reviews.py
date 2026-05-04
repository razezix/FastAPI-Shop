from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.application.reviews.create_review import CreateReviewInput, CreateReviewUseCase
from src.application.reviews.delete_review import DeleteReviewUseCase
from src.application.reviews.list_reviews import ListReviewsUseCase
from src.core.exceptions import DuplicateReview, EntityNotFound
from src.presentation.api.deps import CurrentUser, get_order_repo, get_product_repo, get_review_repo
from src.presentation.schemas.review import (
    CreateReviewRequest,
    PaginatedReviewsResponse,
    ReviewResponse,
)

router = APIRouter(prefix="/products", tags=["reviews"])


def _to_response(r) -> ReviewResponse:
    return ReviewResponse(
        id=r.id,
        product_id=r.product_id,
        user_id=r.user_id,
        rating=r.rating,
        title=r.title,
        body=r.body,
        is_verified_purchase=r.is_verified_purchase,
        created_at=r.created_at,
    )


@router.get("/{product_id}/reviews", response_model=PaginatedReviewsResponse)
async def list_reviews(
    product_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    review_repo=Depends(get_review_repo),
):
    use_case = ListReviewsUseCase(review_repo)
    result = await use_case.execute(product_id, page=page, page_size=page_size)
    return PaginatedReviewsResponse(
        items=[_to_response(r) for r in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.post("/{product_id}/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    product_id: UUID,
    body: CreateReviewRequest,
    current_user: CurrentUser,
    review_repo=Depends(get_review_repo),
    product_repo=Depends(get_product_repo),
    order_repo=Depends(get_order_repo),
):
    try:
        use_case = CreateReviewUseCase(review_repo, product_repo, order_repo)
        review = await use_case.execute(
            CreateReviewInput(
                user_id=current_user.id,
                product_id=product_id,
                rating=body.rating,
                title=body.title,
                body=body.body,
            )
        )
        return _to_response(review)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateReview as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    current_user: CurrentUser,
    review_repo=Depends(get_review_repo),
    product_repo=Depends(get_product_repo),
):
    try:
        use_case = DeleteReviewUseCase(review_repo, product_repo)
        await use_case.execute(review_id, current_user.id, current_user.role)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
