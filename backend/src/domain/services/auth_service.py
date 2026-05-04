from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.users.enums import UserRole


class AbstractAuthService(ABC):
    @abstractmethod
    def hash_password(self, plain: str) -> str: ...

    @abstractmethod
    def verify_password(self, plain: str, hashed: str) -> bool: ...

    @abstractmethod
    def create_access_token(self, user_id: UUID, role: UserRole) -> str: ...

    @abstractmethod
    def create_refresh_token(self, user_id: UUID) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> dict: ...
