from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.domain.payments.entities import PaymentStatus


class PaymentIntentResponse(BaseModel):
    payment_id: str
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str


class ConfirmPaymentRequest(BaseModel):
    payment_intent_id: str
    payment_method: str = "card"


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_intent_id: str
    payment_method: str
    created_at: datetime
