from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.core.exceptions import AccessDenied, EntityNotFound
from src.domain.orders.enums import OrderStatus
from src.domain.orders.repositories import AbstractOrderRepository
from src.domain.payments.entities import Payment, PaymentStatus
from src.domain.payments.repositories import AbstractPaymentRepository
from src.domain.services.payment_service import AbstractPaymentService


@dataclass
class PaymentIntentOutput:
    payment_id: str
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str


class CreatePaymentIntentUseCase:
    def __init__(
        self,
        order_repo: AbstractOrderRepository,
        payment_repo: AbstractPaymentRepository,
        payment_service: AbstractPaymentService,
    ) -> None:
        self._orders = order_repo
        self._payments = payment_repo
        self._payment_service = payment_service

    async def execute(self, order_id: UUID, user_id: UUID) -> PaymentIntentOutput:
        order = await self._orders.get_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order {order_id} not found")
        if order.user_id != user_id:
            raise AccessDenied("Cannot pay for another user's order")
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Order cannot be paid in status {order.status}")

        existing = await self._payments.get_by_order_id(order_id)
        if existing and existing.status == PaymentStatus.COMPLETED:
            raise ValueError("Order is already paid")

        intent = await self._payment_service.create_payment_intent(
            amount=order.total_amount,
            currency="USD",
            metadata={"order_id": str(order_id), "user_id": str(user_id)},
        )

        now = datetime.now(timezone.utc)
        payment = Payment(
            id=uuid4(),
            order_id=order_id,
            user_id=user_id,
            amount=order.total_amount,
            currency="USD",
            status=PaymentStatus.PENDING,
            payment_intent_id=intent["id"],
            payment_method="card",
            gateway_response=intent,
            created_at=now,
            updated_at=now,
        )
        created = await self._payments.create(payment)
        return PaymentIntentOutput(
            payment_id=str(created.id),
            payment_intent_id=intent["id"],
            client_secret=intent["client_secret"],
            amount=float(order.total_amount),
            currency="USD",
        )
