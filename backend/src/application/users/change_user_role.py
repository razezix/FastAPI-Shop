from uuid import UUID

from src.domain.users.entities import User
from src.domain.users.enums import UserRole
from src.domain.users.repositories import AbstractUserRepository


class ChangeUserRoleUseCase:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._repo = user_repo

    async def execute(self, user_id: UUID, new_role: UserRole) -> User:
        return await self._repo.change_role(user_id, new_role)


class SetUserActiveUseCase:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._repo = user_repo

    async def execute(self, user_id: UUID, is_active: bool) -> User:
        return await self._repo.set_active(user_id, is_active)
