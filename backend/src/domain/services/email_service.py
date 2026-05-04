from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID


class AbstractEmailService(ABC):
    @abstractmethod
    async def send_order_confirmation(self, to: str, order_id: UUID, total: Decimal) -> None: ...

    @abstractmethod
    async def send_order_status_update(self, to: str, order_id: UUID, new_status: str) -> None: ...

    @abstractmethod
    async def send_welcome_email(self, to: str, first_name: str) -> None: ...
