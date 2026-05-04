from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.payments.entities import Payment


class AbstractPaymentRepository(ABC):
    @abstractmethod
    async def create(self, payment: Payment) -> Payment: ...

    @abstractmethod
    async def get_by_id(self, payment_id: UUID) -> Payment | None: ...

    @abstractmethod
    async def get_by_intent_id(self, intent_id: str) -> Payment | None: ...

    @abstractmethod
    async def get_by_order_id(self, order_id: UUID) -> Payment | None: ...

    @abstractmethod
    async def update(self, payment: Payment) -> Payment: ...
