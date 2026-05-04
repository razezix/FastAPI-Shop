from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.application.orders.create_order import PlaceOrderInput, PlaceOrderUseCase
from src.application.orders.get_order import GetOrderUseCase
from src.application.orders.list_my_orders import ListMyOrdersUseCase
from src.application.orders.list_orders import ListOrdersUseCase
from src.application.orders.update_order_status import UpdateOrderStatusUseCase
from src.core.exceptions import (
    CartIsEmpty,
    EntityNotFound,
    InvalidDiscountCode,
    InvalidOrderStatusTransition,
)
from src.domain.orders.enums import OrderStatus
from src.domain.users.enums import UserRole
from src.presentation.api.deps import (
    CurrentUser,
    ManagerOrAbove,
    get_cart_repo,
    get_discount_repo,
    get_order_repo,
    get_product_repo,
)
from src.presentation.schemas.order import (
    OrderItemResponse,
    OrderResponse,
    PaginatedOrdersResponse,
    PlaceOrderRequest,
    UpdateOrderStatusRequest,
)

router = APIRouter(prefix="/orders", tags=["orders"])


def _item_response(item) -> OrderItemResponse:
    return OrderItemResponse(
        id=item.id,
        product_id=item.product_id,
        product_name=item.product_name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        subtotal=item.subtotal,
    )


def _order_response(order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        items=[_item_response(i) for i in order.items],
        subtotal=order.subtotal,
        discount_amount=order.discount_amount,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        notes=order.notes,
        created_at=order.created_at,
    )


@router.post("", response_model=OrderResponse, status_code=201)
async def place_order(
    body: PlaceOrderRequest,
    current_user: CurrentUser,
    order_repo=Depends(get_order_repo),
    cart_repo=Depends(get_cart_repo),
    product_repo=Depends(get_product_repo),
    discount_repo=Depends(get_discount_repo),
):
    try:
        use_case = PlaceOrderUseCase(order_repo, cart_repo, product_repo, discount_repo)
        order = await use_case.execute(
            PlaceOrderInput(
                user_id=current_user.id,
                shipping_address=body.shipping_address,
                discount_code=body.discount_code,
                notes=body.notes,
            )
        )
        return _order_response(order)
    except CartIsEmpty as e:
        raise HTTPException(status_code=422, detail=str(e))
    except (InvalidDiscountCode, EntityNotFound) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=PaginatedOrdersResponse)
async def list_orders(
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: OrderStatus | None = Query(default=None),
    order_repo=Depends(get_order_repo),
):
    if current_user.is_manager_or_above():
        use_case = ListOrdersUseCase(order_repo)
        result = await use_case.execute(page=page, page_size=page_size, status=status)
    else:
        use_case = ListMyOrdersUseCase(order_repo)
        result = await use_case.execute(current_user.id, page=page, page_size=page_size)

    return PaginatedOrdersResponse(
        items=[_order_response(o) for o in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: CurrentUser,
    order_repo=Depends(get_order_repo),
):
    try:
        use_case = GetOrderUseCase(order_repo)
        order = await use_case.execute(order_id, current_user.id, current_user.role)
        return _order_response(order)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    body: UpdateOrderStatusRequest,
    current_user: CurrentUser,
    order_repo=Depends(get_order_repo),
):
    try:
        use_case = UpdateOrderStatusUseCase(order_repo)
        order = await use_case.execute(
            order_id=order_id,
            new_status=body.status,
            acting_user_id=current_user.id,
            acting_user_role=current_user.role,
        )
        return _order_response(order)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOrderStatusTransition as e:
        raise HTTPException(status_code=422, detail=str(e))
