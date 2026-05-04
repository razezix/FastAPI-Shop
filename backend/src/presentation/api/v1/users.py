from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.core.exceptions import EntityNotFound
from src.presentation.api.deps import AdminOnly, CurrentUser, get_user_repo
from src.presentation.schemas.user import (
    ChangeRoleRequest,
    UpdateProfileRequest,
    UserListResponse,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


def _to_response(u) -> UserResponse:
    return UserResponse(
        id=u.id,
        email=u.email,
        first_name=u.first_name,
        last_name=u.last_name,
        role=u.role,
        is_active=u.is_active,
        is_verified=u.is_verified,
        created_at=u.created_at,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return _to_response(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    body: UpdateProfileRequest,
    current_user: CurrentUser,
    user_repo=Depends(get_user_repo),
):
    if body.first_name:
        current_user.first_name = body.first_name
    if body.last_name:
        current_user.last_name = body.last_name
    updated = await user_repo.update(current_user)
    return _to_response(updated)


@router.get("", response_model=UserListResponse)
async def list_users(
    _: AdminOnly,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_repo=Depends(get_user_repo),
):
    skip = (page - 1) * page_size
    users, total = await user_repo.list_all(skip=skip, limit=page_size)
    pages = max(1, (total + page_size - 1) // page_size)
    return UserListResponse(
        items=[_to_response(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    _: AdminOnly,
    user_repo=Depends(get_user_repo),
):
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_response(user)


@router.put("/{user_id}/role", response_model=UserResponse)
async def change_role(
    user_id: UUID,
    body: ChangeRoleRequest,
    _: AdminOnly,
    user_repo=Depends(get_user_repo),
):
    try:
        user = await user_repo.change_role(user_id, body.role)
        return _to_response(user)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}/ban", response_model=UserResponse)
async def ban_user(
    user_id: UUID,
    is_active: bool,
    _: AdminOnly,
    user_repo=Depends(get_user_repo),
):
    try:
        user = await user_repo.set_active(user_id, is_active)
        return _to_response(user)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
