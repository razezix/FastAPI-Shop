from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.wishlist.entities import WishlistItem


class AbstractWishlistRepository(ABC):
    @abstractmethod
    async def add(self, item: WishlistItem) -> WishlistItem: ...

    @abstractmethod
    async def remove(self, user_id: UUID, product_id: UUID) -> None: ...

    @abstractmethod
    async def get(self, user_id: UUID, product_id: UUID) -> WishlistItem | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> list[WishlistItem]: ...
