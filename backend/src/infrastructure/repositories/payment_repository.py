from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.payments.entities import Payment, PaymentStatus
from src.domain.payments.repositories import AbstractPaymentRepository
from src.infrastructure.database.models.payment import PaymentModel


def _to_entity(m: PaymentModel) -> Payment:
    return Payment(
        id=UUID(m.id),
        order_id=UUID(m.order_id),
        user_id=UUID(m.user_id),
        amount=m.amount,
        currency=m.currency,
        status=PaymentStatus(m.status),
        payment_intent_id=m.payment_intent_id,
        payment_method=m.payment_method,
        gateway_response=m.gateway_response,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SQLAlchemyPaymentRepository(AbstractPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, payment: Payment) -> Payment:
        model = PaymentModel(
            id=str(payment.id),
            order_id=str(payment.order_id),
            user_id=str(payment.user_id),
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status.value,
            payment_intent_id=payment.payment_intent_id,
            payment_method=payment.payment_method,
            gateway_response=payment.gateway_response,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == str(payment_id))
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_intent_id(self, intent_id: str) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.payment_intent_id == intent_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_order_id(self, order_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.order_id == str(order_id))
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update(self, payment: Payment) -> Payment:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == str(payment.id))
        )
        model = result.scalar_one()
        model.status = payment.status.value
        model.gateway_response = payment.gateway_response
        await self._session.flush()
        return _to_entity(model)
