from abc import ABC, abstractmethod
from decimal import Decimal


class AbstractPaymentService(ABC):
    @abstractmethod
    async def create_payment_intent(self, amount: Decimal, currency: str, metadata: dict) -> dict: ...

    @abstractmethod
    async def confirm_payment(self, intent_id: str, payment_method: str) -> dict: ...

    @abstractmethod
    async def refund(self, intent_id: str, amount: Decimal) -> dict: ...

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool: ...
