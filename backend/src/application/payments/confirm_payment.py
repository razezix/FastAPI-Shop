from src.core.exceptions import EntityNotFound, PaymentFailed
from src.domain.orders.enums import OrderStatus
from src.domain.orders.repositories import AbstractOrderRepository
from src.domain.payments.entities import Payment, PaymentStatus
from src.domain.payments.repositories import AbstractPaymentRepository
from src.domain.products.repositories import AbstractProductRepository
from src.domain.services.cache_service import AbstractCacheService
from src.domain.services.email_service import AbstractEmailService
from src.domain.services.payment_service import AbstractPaymentService
from src.domain.users.repositories import AbstractUserRepository


class ConfirmPaymentUseCase:
    def __init__(
        self,
        payment_repo: AbstractPaymentRepository,
        order_repo: AbstractOrderRepository,
        product_repo: AbstractProductRepository,
        user_repo: AbstractUserRepository,
        payment_service: AbstractPaymentService,
        email_service: AbstractEmailService,
        cache: AbstractCacheService,
    ) -> None:
        self._payments = payment_repo
        self._orders = order_repo
        self._products = product_repo
        self._users = user_repo
        self._payment_service = payment_service
        self._email_service = email_service
        self._cache = cache

    async def execute(self, payment_intent_id: str, payment_method: str) -> Payment:
        payment = await self._payments.get_by_intent_id(payment_intent_id)
        if not payment:
            raise EntityNotFound(f"Payment intent {payment_intent_id} not found")

        payment.status = PaymentStatus.PROCESSING
        await self._payments.update(payment)

        try:
            result = await self._payment_service.confirm_payment(payment_intent_id, payment_method)
            payment.status = PaymentStatus.COMPLETED
            payment.payment_method = payment_method
            payment.gateway_response = result
            await self._payments.update(payment)

            # Advance order to PAID
            order = await self._orders.get_by_id(payment.order_id)
            if order:
                order.transition_to(OrderStatus.PAID)
                await self._orders.update(order)

                # Increment purchase counts for analytics
                for item in order.items:
                    await self._products.increment_purchase_count(item.product_id, item.quantity)

                # Invalidate popular-this-week cache
                await self._cache.invalidate_pattern("popular_this_week:*")

                # Send confirmation email
                user = await self._users.get_by_id(order.user_id)
                if user:
                    try:
                        await self._email_service.send_order_confirmation(
                            user.email, order.id, order.total_amount
                        )
                    except Exception:
                        pass

        except PaymentFailed:
            payment.status = PaymentStatus.FAILED
            await self._payments.update(payment)
            raise

        return payment
