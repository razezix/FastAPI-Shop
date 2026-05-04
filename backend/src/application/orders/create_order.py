from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from src.core.exceptions import (
    CartIsEmpty,
    DiscountExpired,
    DiscountUsageLimitReached,
    EntityNotFound,
    InvalidDiscountCode,
)
from src.domain.cart.repositories import AbstractCartRepository
from src.domain.discounts.repositories import AbstractDiscountRepository
from src.domain.orders.entities import Order, OrderItem
from src.domain.orders.enums import OrderStatus
from src.domain.orders.repositories import AbstractOrderRepository
from src.domain.products.repositories import AbstractProductRepository


@dataclass
class PlaceOrderInput:
    user_id: UUID
    shipping_address: str
    discount_code: str | None = None
    notes: str | None = None


class PlaceOrderUseCase:
    def __init__(
        self,
        order_repo: AbstractOrderRepository,
        cart_repo: AbstractCartRepository,
        product_repo: AbstractProductRepository,
        discount_repo: AbstractDiscountRepository,
    ) -> None:
        self._orders = order_repo
        self._carts = cart_repo
        self._products = product_repo
        self._discounts = discount_repo

    async def execute(self, input: PlaceOrderInput) -> Order:
        cart = await self._carts.get_by_user_id(input.user_id)
        if not cart or cart.is_empty:
            raise CartIsEmpty("Cart is empty")

        # Validate stock and decrement for each item
        order_items: list[OrderItem] = []
        subtotal = Decimal("0.00")
        for cart_item in cart.items:
            await self._products.decrement_stock(cart_item.product_id, cart_item.quantity)
            product = await self._products.get_by_id(cart_item.product_id, include_archived=True)
            if not product:
                raise EntityNotFound(f"Product {cart_item.product_id} not found")
            item_subtotal = cart_item.unit_price * cart_item.quantity
            order_items.append(
                OrderItem(
                    id=uuid4(),
                    order_id=uuid4(),  # placeholder, set below
                    product_id=cart_item.product_id,
                    product_name=product.name,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                )
            )
            subtotal += item_subtotal

        # Apply discount
        discount_amount = Decimal("0.00")
        discount_id: UUID | None = None
        if input.discount_code:
            discount = await self._discounts.get_by_code(input.discount_code)
            if not discount:
                raise InvalidDiscountCode(f"Discount code '{input.discount_code}' is invalid")
            if not discount.is_active:
                raise InvalidDiscountCode("Discount code is no longer active")
            now = datetime.now(timezone.utc)
            if discount.valid_until and discount.valid_until < now:
                raise DiscountExpired("Discount code has expired")
            if discount.valid_from > now:
                raise InvalidDiscountCode("Discount code is not yet valid")
            if discount.usage_limit is not None and discount.used_count >= discount.usage_limit:
                raise DiscountUsageLimitReached("Discount code usage limit reached")
            if discount.min_order_amount and subtotal < discount.min_order_amount:
                raise InvalidDiscountCode(
                    f"Minimum order amount for this discount is ${discount.min_order_amount}"
                )
            discount_amount = discount.calculate_discount(subtotal)
            discount_id = discount.id
            await self._discounts.increment_usage(discount.id)

        total_amount = max(Decimal("0.00"), subtotal - discount_amount)
        order_id = uuid4()

        # Fix order_id on items
        for item in order_items:
            item.order_id = order_id

        now = datetime.now(timezone.utc)
        order = Order(
            id=order_id,
            user_id=input.user_id,
            status=OrderStatus.PENDING,
            items=order_items,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_amount=total_amount,
            discount_id=discount_id,
            shipping_address=input.shipping_address,
            notes=input.notes,
            created_at=now,
            updated_at=now,
        )
        created_order = await self._orders.create(order)
        await self._carts.clear(cart.id)
        return created_order
