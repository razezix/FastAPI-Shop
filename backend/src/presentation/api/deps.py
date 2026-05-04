from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.exceptions import AccessDenied, InvalidCredentials, UserIsBanned
from src.domain.users.entities import User
from src.domain.users.enums import UserRole
from src.infrastructure.auth.jwt_service import JWTAuthService
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.analytics_repository import SQLAlchemyAnalyticsRepository
from src.infrastructure.repositories.cart_repository import SQLAlchemyCartRepository
from src.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from src.infrastructure.repositories.discount_repository import SQLAlchemyDiscountRepository
from src.infrastructure.repositories.order_repository import SQLAlchemyOrderRepository
from src.infrastructure.repositories.payment_repository import SQLAlchemyPaymentRepository
from src.infrastructure.repositories.product_repository import SQLAlchemyProductRepository
from src.infrastructure.repositories.review_repository import SQLAlchemyReviewRepository
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.repositories.wishlist_repository import SQLAlchemyWishlistRepository
from src.infrastructure.services.mock_payment_service import MockPaymentService
from src.infrastructure.services.redis_cache_service import RedisCacheService
from src.infrastructure.services.smtp_email_service import SMTPEmailService

from sqlalchemy.ext.asyncio import AsyncSession

bearer_scheme = HTTPBearer(auto_error=False)


# ── Session ──────────────────────────────────────────────────────────────────

DbSession = Annotated[AsyncSession, Depends(get_db)]


# ── Repositories ─────────────────────────────────────────────────────────────

def get_user_repo(db: DbSession) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


def get_product_repo(db: DbSession) -> SQLAlchemyProductRepository:
    return SQLAlchemyProductRepository(db)


def get_category_repo(db: DbSession) -> SQLAlchemyCategoryRepository:
    return SQLAlchemyCategoryRepository(db)


def get_cart_repo(db: DbSession) -> SQLAlchemyCartRepository:
    return SQLAlchemyCartRepository(db)


def get_order_repo(db: DbSession) -> SQLAlchemyOrderRepository:
    return SQLAlchemyOrderRepository(db)


def get_payment_repo(db: DbSession) -> SQLAlchemyPaymentRepository:
    return SQLAlchemyPaymentRepository(db)


def get_review_repo(db: DbSession) -> SQLAlchemyReviewRepository:
    return SQLAlchemyReviewRepository(db)


def get_discount_repo(db: DbSession) -> SQLAlchemyDiscountRepository:
    return SQLAlchemyDiscountRepository(db)


def get_wishlist_repo(db: DbSession) -> SQLAlchemyWishlistRepository:
    return SQLAlchemyWishlistRepository(db)


def get_analytics_repo(db: DbSession) -> SQLAlchemyAnalyticsRepository:
    return SQLAlchemyAnalyticsRepository(db)


# ── Services ─────────────────────────────────────────────────────────────────

def get_auth_service() -> JWTAuthService:
    return JWTAuthService()


def get_payment_service() -> MockPaymentService:
    return MockPaymentService()


def get_email_service() -> SMTPEmailService:
    return SMTPEmailService()


def get_cache_service(request: Request) -> RedisCacheService:
    return request.app.state.cache


# ── Auth dependencies ─────────────────────────────────────────────────────────

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    user_repo: Annotated[SQLAlchemyUserRepository, Depends(get_user_repo)],
    auth_service: Annotated[JWTAuthService, Depends(get_auth_service)],
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        from src.application.auth.get_current_user import GetCurrentUserUseCase
        use_case = GetCurrentUserUseCase(user_repo, auth_service)
        return await use_case.execute(credentials.credentials)
    except (InvalidCredentials, UserIsBanned) as e:
        raise HTTPException(status_code=401, detail=str(e))


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    def dependency(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return Depends(dependency)


def require_manager_or_above(current_user: CurrentUser) -> User:
    if not current_user.is_manager_or_above():
        raise HTTPException(status_code=403, detail="Manager or Admin role required")
    return current_user


def require_admin(current_user: CurrentUser) -> User:
    if not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user


ManagerOrAbove = Annotated[User, Depends(require_manager_or_above)]
AdminOnly = Annotated[User, Depends(require_admin)]
