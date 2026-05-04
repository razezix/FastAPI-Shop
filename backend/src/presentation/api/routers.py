from fastapi import FastAPI

from src.presentation.api.v1 import (
    analytics,
    auth,
    cart,
    categories,
    discounts,
    orders,
    payments,
    products,
    reviews,
    users,
    wishlist,
)

_V1_PREFIX = "/api/v1"


def register_routers(app: FastAPI) -> None:
    for module in [auth, users, products, categories, cart, orders, payments, reviews, discounts, wishlist, analytics]:
        app.include_router(module.router, prefix=_V1_PREFIX)
