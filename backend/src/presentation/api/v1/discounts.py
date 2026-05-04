from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.application.discounts.create_discount import CreateDiscountInput, CreateDiscountUseCase
from src.application.discounts.validate_discount import ValidateDiscountUseCase
from src.core.exceptions import (
    DiscountExpired,
    DiscountUsageLimitReached,
    InvalidDiscountCode,
)
from src.presentation.api.deps import CurrentUser, ManagerOrAbove, get_discount_repo
from src.presentation.schemas.discount import (
    CreateDiscountRequest,
    DiscountResponse,
    PaginatedDiscountsResponse,
    ValidateDiscountRequest,
    ValidateDiscountResponse,
)

router = APIRouter(prefix="/discounts", tags=["discounts"])


def _to_response(d) -> DiscountResponse:
    return DiscountResponse(
        id=d.id,
        code=d.code,
        discount_type=d.discount_type,
        value=d.value,
        min_order_amount=d.min_order_amount,
        max_discount_amount=d.max_discount_amount,
        usage_limit=d.usage_limit,
        used_count=d.used_count,
        is_active=d.is_active,
        valid_from=d.valid_from,
        valid_until=d.valid_until,
    )


@router.get("", response_model=PaginatedDiscountsResponse)
async def list_discounts(
    _: ManagerOrAbove,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    discount_repo=Depends(get_discount_repo),
):
    skip = (page - 1) * page_size
    items, total = await discount_repo.list_all(skip=skip, limit=page_size)
    pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedDiscountsResponse(
        items=[_to_response(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("", response_model=DiscountResponse, status_code=201)
async def create_discount(
    body: CreateDiscountRequest,
    current_user: ManagerOrAbove,
    discount_repo=Depends(get_discount_repo),
):
    use_case = CreateDiscountUseCase(discount_repo)
    discount = await use_case.execute(
        CreateDiscountInput(
            code=body.code,
            discount_type=body.discount_type,
            value=body.value,
            created_by=current_user.id,
            min_order_amount=body.min_order_amount,
            max_discount_amount=body.max_discount_amount,
            usage_limit=body.usage_limit,
            valid_until=body.valid_until,
        )
    )
    return _to_response(discount)


@router.delete("/{discount_id}", status_code=204)
async def deactivate_discount(
    discount_id: UUID,
    _: ManagerOrAbove,
    discount_repo=Depends(get_discount_repo),
):
    await discount_repo.deactivate(discount_id)


@router.post("/validate", response_model=ValidateDiscountResponse)
async def validate_discount(
    body: ValidateDiscountRequest,
    _: CurrentUser,
    discount_repo=Depends(get_discount_repo),
):
    try:
        use_case = ValidateDiscountUseCase(discount_repo)
        result = await use_case.execute(body.code, body.order_amount)
        return ValidateDiscountResponse(
            discount=_to_response(result.discount),
            discount_amount=result.discount_amount,
        )
    except (InvalidDiscountCode, DiscountExpired, DiscountUsageLimitReached) as e:
        raise HTTPException(status_code=422, detail=str(e))
