from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.users.enums import UserRole


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def is_manager_or_above(self) -> bool:
        return self.role in (UserRole.MANAGER, UserRole.ADMIN)

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
