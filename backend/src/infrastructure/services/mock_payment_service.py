import hashlib
import hmac
import json
import random
from decimal import Decimal
from uuid import uuid4

from src.core.config import get_settings
from src.core.exceptions import PaymentFailed
from src.domain.services.payment_service import AbstractPaymentService


class MockPaymentService(AbstractPaymentService):
    def __init__(self) -> None:
        self._settings = get_settings()

    async def create_payment_intent(self, amount: Decimal, currency: str, metadata: dict) -> dict:
        intent_id = f"pi_mock_{uuid4().hex}"
        return {
            "id": intent_id,
            "amount": float(amount),
            "currency": currency,
            "status": "requires_payment_method",
            "client_secret": f"{intent_id}_secret_{uuid4().hex[:16]}",
            "metadata": metadata,
        }

    async def confirm_payment(self, intent_id: str, payment_method: str) -> dict:
        # 90% success rate simulation
        if random.random() < 0.1:
            raise PaymentFailed("Payment declined by mock gateway")
        return {
            "id": intent_id,
            "status": "succeeded",
            "payment_method": payment_method,
            "amount_received": None,
        }

    async def refund(self, intent_id: str, amount: Decimal) -> dict:
        return {
            "id": f"re_mock_{uuid4().hex}",
            "payment_intent": intent_id,
            "amount": float(amount),
            "status": "succeeded",
        }

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        secret = self._settings.WEBHOOK_SECRET.encode()
        expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
