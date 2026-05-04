from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.cart.add_cart_item import AddCartItemInput, AddCartItemUseCase
from src.application.cart.clear_cart import ClearCartUseCase
from src.application.cart.get_cart import GetCartUseCase
from src.application.cart.remove_cart_item import RemoveCartItemUseCase
from src.application.cart.update_cart_item import UpdateCartItemInput, UpdateCartItemUseCase
from src.core.exceptions import AccessDenied, EntityNotFound, InsufficientStock, ProductIsArchived
from src.presentation.api.deps import CurrentUser, get_cart_repo, get_product_repo
from src.presentation.schemas.cart import (
    AddCartItemRequest,
    CartItemResponse,
    CartResponse,
    UpdateCartItemRequest,
)

router = APIRouter(prefix="/cart", tags=["cart"])


def _cart_response(cart) -> CartResponse:
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
                added_at=item.added_at,
            )
            for item in cart.items
        ],
        total=cart.total,
    )


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: CurrentUser,
    cart_repo=Depends(get_cart_repo),
):
    use_case = GetCartUseCase(cart_repo)
    cart = await use_case.execute(current_user.id)
    return _cart_response(cart)


@router.post("/items", response_model=CartResponse, status_code=201)
async def add_item(
    body: AddCartItemRequest,
    current_user: CurrentUser,
    cart_repo=Depends(get_cart_repo),
    product_repo=Depends(get_product_repo),
):
    try:
        use_case = AddCartItemUseCase(cart_repo, product_repo)
        cart = await use_case.execute(
            AddCartItemInput(
                user_id=current_user.id,
                product_id=body.product_id,
                quantity=body.quantity,
            )
        )
        return _cart_response(cart)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (InsufficientStock, ProductIsArchived) as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_item(
    item_id: UUID,
    body: UpdateCartItemRequest,
    current_user: CurrentUser,
    cart_repo=Depends(get_cart_repo),
):
    try:
        use_case = UpdateCartItemUseCase(cart_repo)
        cart = await use_case.execute(
            UpdateCartItemInput(
                user_id=current_user.id,
                item_id=item_id,
                quantity=body.quantity,
            )
        )
        return _cart_response(cart)
    except (EntityNotFound, AccessDenied) as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_item(
    item_id: UUID,
    current_user: CurrentUser,
    cart_repo=Depends(get_cart_repo),
):
    try:
        use_case = RemoveCartItemUseCase(cart_repo)
        cart = await use_case.execute(current_user.id, item_id)
        return _cart_response(cart)
    except (EntityNotFound, AccessDenied) as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("", response_model=CartResponse)
async def clear_cart(
    current_user: CurrentUser,
    cart_repo=Depends(get_cart_repo),
):
    use_case = ClearCartUseCase(cart_repo)
    cart = await use_case.execute(current_user.id)
    return _cart_response(cart)
