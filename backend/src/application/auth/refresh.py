from dataclasses import dataclass
from uuid import UUID

from src.core.exceptions import InvalidCredentials, UserIsBanned
from src.domain.services.auth_service import AbstractAuthService
from src.domain.users.repositories import AbstractUserRepository


@dataclass
class RefreshOutput:
    access_token: str
    token_type: str = "bearer"


class RefreshTokenUseCase:
    def __init__(self, user_repo: AbstractUserRepository, auth_service: AbstractAuthService) -> None:
        self._user_repo = user_repo
        self._auth_service = auth_service

    async def execute(self, refresh_token: str) -> RefreshOutput:
        payload = self._auth_service.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidCredentials("Not a refresh token")

        user = await self._user_repo.get_by_id(UUID(payload["sub"]))
        if not user:
            raise InvalidCredentials("User not found")
        if not user.is_active:
            raise UserIsBanned("Account is banned")

        access_token = self._auth_service.create_access_token(user.id, user.role)
        return RefreshOutput(access_token=access_token)
