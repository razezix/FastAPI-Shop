from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.application.auth.login_user import LoginUseCase
from src.application.auth.refresh import RefreshTokenUseCase
from src.application.auth.register_user import RegisterInput, RegisterUseCase
from src.core.exceptions import InvalidCredentials, UserAlreadyExists, UserIsBanned
from src.presentation.api.deps import (
    CurrentUser,
    get_auth_service,
    get_email_service,
    get_user_repo,
)
from src.presentation.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from src.presentation.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    user_repo=Depends(get_user_repo),
    auth_service=Depends(get_auth_service),
    email_service=Depends(get_email_service),
):
    try:
        use_case = RegisterUseCase(user_repo, auth_service, email_service)
        result = await use_case.execute(
            RegisterInput(
                email=body.email,
                password=body.password,
                first_name=body.first_name,
                last_name=body.last_name,
            )
        )
        return TokenResponse(access_token=result.access_token, refresh_token=result.refresh_token)
    except UserAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    user_repo=Depends(get_user_repo),
    auth_service=Depends(get_auth_service),
):
    try:
        use_case = LoginUseCase(user_repo, auth_service)
        result = await use_case.execute(body.email, body.password)
        return TokenResponse(access_token=result.access_token, refresh_token=result.refresh_token)
    except (InvalidCredentials, UserIsBanned) as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    body: RefreshRequest,
    user_repo=Depends(get_user_repo),
    auth_service=Depends(get_auth_service),
):
    try:
        use_case = RefreshTokenUseCase(user_repo, auth_service)
        result = await use_case.execute(body.refresh_token)
        return AccessTokenResponse(access_token=result.access_token)
    except (InvalidCredentials, UserIsBanned) as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
    )
