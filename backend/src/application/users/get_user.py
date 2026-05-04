from uuid import UUID

from src.core.exceptions import EntityNotFound
from src.domain.users.entities import User
from src.domain.users.repositories import AbstractUserRepository


class GetUserUseCase:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._repo = user_repo

    async def execute(self, user_id: UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise EntityNotFound(f"User {user_id} not found")
        return user
