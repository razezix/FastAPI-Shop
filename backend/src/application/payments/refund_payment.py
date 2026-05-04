from uuid import UUID

from src.core.exceptions import EntityNotFound
from src.domain.orders.enums import OrderStatus
from src.domain.orders.repositories import AbstractOrderRepository
from src.domain.payments.entities import Payment, PaymentStatus
from src.domain.payments.repositories import AbstractPaymentRepository
from src.domain.services.payment_service import AbstractPaymentService


class RefundPaymentUseCase:
    def __init__(
        self,
        payment_repo: AbstractPaymentRepository,
        order_repo: AbstractOrderRepository,
        payment_service: AbstractPaymentService,
    ) -> None:
        self._payments = payment_repo
        self._orders = order_repo
        self._payment_service = payment_service

    async def execute(self, payment_id: UUID) -> Payment:
        payment = await self._payments.get_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment {payment_id} not found")
        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Only completed payments can be refunded")

        result = await self._payment_service.refund(payment.payment_intent_id, payment.amount)
        payment.status = PaymentStatus.REFUNDED
        payment.gateway_response = result
        await self._payments.update(payment)

        order = await self._orders.get_by_id(payment.order_id)
        if order and order.status == OrderStatus.PAID:
            order.transition_to(OrderStatus.CANCELLED)
            await self._orders.update(order)

        return payment
