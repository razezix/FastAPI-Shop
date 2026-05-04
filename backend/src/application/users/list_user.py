from dataclasses import dataclass

from src.domain.users.entities import User
from src.domain.users.repositories import AbstractUserRepository


@dataclass
class UserListResult:
    items: list[User]
    total: int
    page: int
    page_size: int
    pages: int


class ListUsersUseCase:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._repo = user_repo

    async def execute(self, page: int = 1, page_size: int = 20) -> UserListResult:
        skip = (page - 1) * page_size
        items, total = await self._repo.list_all(skip=skip, limit=page_size)
        pages = max(1, (total + page_size - 1) // page_size)
        return UserListResult(items=items, total=total, page=page, page_size=page_size, pages=pages)
