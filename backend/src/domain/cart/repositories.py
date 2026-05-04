from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.cart.entities import Cart, CartItem


class AbstractCartRepository(ABC):
    @abstractmethod
    async def get_or_create(self, user_id: UUID) -> Cart: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Cart | None: ...

    @abstractmethod
    async def add_item(self, cart_id: UUID, item: CartItem) -> CartItem: ...

    @abstractmethod
    async def get_item(self, item_id: UUID) -> CartItem | None: ...

    @abstractmethod
    async def update_item_quantity(self, item_id: UUID, quantity: int) -> CartItem: ...

    @abstractmethod
    async def remove_item(self, item_id: UUID) -> None: ...

    @abstractmethod
    async def clear(self, cart_id: UUID) -> None: ...
