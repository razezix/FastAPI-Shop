from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import get_settings
from src.core.exceptions import (
    AccessDenied,
    CartIsEmpty,
    DiscountExpired,
    DiscountUsageLimitReached,
    DomainException,
    DuplicateReview,
    EntityNotFound,
    InsufficientStock,
    InvalidCredentials,
    InvalidDiscountCode,
    InvalidOrderStatusTransition,
    InvalidRating,
    OrderCannotBeCancelled,
    PaymentFailed,
    ProductIsArchived,
    UserAlreadyExists,
    UserIsBanned,
)
from src.infrastructure.database.session import init_db
from src.infrastructure.services.redis_cache_service import RedisCacheService
from src.presentation.api.routers import register_routers
from src.presentation.api.v1.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    init_db()

    cache = RedisCacheService(settings.REDIS_URL)
    await cache.connect()
    app.state.cache = cache

    yield

    await cache.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Online Shop API",
        version="1.0.0",
        description="Clean Architecture online shop with RBAC, payments, reviews, discounts & analytics",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(EntityNotFound)
    async def not_found_handler(request: Request, exc: EntityNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(AccessDenied)
    async def access_denied_handler(request: Request, exc: AccessDenied):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(InvalidCredentials)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(UserAlreadyExists)
    async def user_exists_handler(request: Request, exc: UserAlreadyExists):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(UserIsBanned)
    async def banned_handler(request: Request, exc: UserIsBanned):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(InsufficientStock)
    async def stock_handler(request: Request, exc: InsufficientStock):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(ProductIsArchived)
    async def archived_handler(request: Request, exc: ProductIsArchived):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(CartIsEmpty)
    async def cart_empty_handler(request: Request, exc: CartIsEmpty):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(InvalidDiscountCode)
    async def discount_invalid_handler(request: Request, exc: InvalidDiscountCode):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(DiscountExpired)
    async def discount_expired_handler(request: Request, exc: DiscountExpired):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(DiscountUsageLimitReached)
    async def discount_limit_handler(request: Request, exc: DiscountUsageLimitReached):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(PaymentFailed)
    async def payment_failed_handler(request: Request, exc: PaymentFailed):
        return JSONResponse(status_code=402, content={"detail": str(exc)})

    @app.exception_handler(InvalidOrderStatusTransition)
    async def order_transition_handler(request: Request, exc: InvalidOrderStatusTransition):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(DuplicateReview)
    async def duplicate_review_handler(request: Request, exc: DuplicateReview):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(DomainException)
    async def domain_handler(request: Request, exc: DomainException):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    # Routers
    app.include_router(health_router, prefix="/api/v1")
    register_routers(app)

    return app


app = create_app()
