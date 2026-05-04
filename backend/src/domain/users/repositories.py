from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.users.entities import User
from src.domain.users.enums import UserRole


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 20) -> tuple[list[User], int]: ...

    @abstractmethod
    async def change_role(self, user_id: UUID, role: UserRole) -> User: ...

    @abstractmethod
    async def set_active(self, user_id: UUID, is_active: bool) -> User: ...
