from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.wishlist.wishlist_use_cases import (
    AddToWishlistUseCase,
    GetWishlistUseCase,
    RemoveFromWishlistUseCase,
)
from src.core.exceptions import EntityNotFound
from src.presentation.api.deps import CurrentUser, get_product_repo, get_wishlist_repo
from src.presentation.schemas.wishlist import WishlistItemResponse, WishlistResponse

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=WishlistResponse)
async def get_wishlist(
    current_user: CurrentUser,
    wishlist_repo=Depends(get_wishlist_repo),
):
    use_case = GetWishlistUseCase(wishlist_repo)
    items = await use_case.execute(current_user.id)
    return WishlistResponse(
        items=[WishlistItemResponse(id=i.id, product_id=i.product_id, added_at=i.added_at) for i in items],
        total=len(items),
    )


@router.post("/{product_id}", response_model=WishlistItemResponse, status_code=201)
async def add_to_wishlist(
    product_id: UUID,
    current_user: CurrentUser,
    wishlist_repo=Depends(get_wishlist_repo),
    product_repo=Depends(get_product_repo),
):
    try:
        use_case = AddToWishlistUseCase(wishlist_repo, product_repo)
        item = await use_case.execute(current_user.id, product_id)
        return WishlistItemResponse(id=item.id, product_id=item.product_id, added_at=item.added_at)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{product_id}", status_code=204)
async def remove_from_wishlist(
    product_id: UUID,
    current_user: CurrentUser,
    wishlist_repo=Depends(get_wishlist_repo),
):
    use_case = RemoveFromWishlistUseCase(wishlist_repo)
    await use_case.execute(current_user.id, product_id)
