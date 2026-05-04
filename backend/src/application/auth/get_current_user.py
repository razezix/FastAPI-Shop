from uuid import UUID

from src.core.exceptions import InvalidCredentials, UserIsBanned
from src.domain.services.auth_service import AbstractAuthService
from src.domain.users.entities import User
from src.domain.users.repositories import AbstractUserRepository


class GetCurrentUserUseCase:
    def __init__(self, user_repo: AbstractUserRepository, auth_service: AbstractAuthService) -> None:
        self._user_repo = user_repo
        self._auth_service = auth_service

    async def execute(self, token: str) -> User:
        payload = self._auth_service.decode_token(token)
        if payload.get("type") != "access":
            raise InvalidCredentials("Not an access token")

        user = await self._user_repo.get_by_id(UUID(payload["sub"]))
        if not user:
            raise InvalidCredentials("User not found")
        if not user.is_active:
            raise UserIsBanned("Account is banned")
        return user
