from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


@dataclass
class Payment:
    id: UUID
    order_id: UUID
    user_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_intent_id: str
    payment_method: str
    gateway_response: dict | None
    created_at: datetime
    updated_at: datetime
