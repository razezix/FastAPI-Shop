from dataclasses import dataclass

from src.core.exceptions import InvalidCredentials, UserIsBanned
from src.domain.services.auth_service import AbstractAuthService
from src.domain.users.repositories import AbstractUserRepository


@dataclass
class LoginOutput:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginUseCase:
    def __init__(self, user_repo: AbstractUserRepository, auth_service: AbstractAuthService) -> None:
        self._user_repo = user_repo
        self._auth_service = auth_service

    async def execute(self, email: str, password: str) -> LoginOutput:
        user = await self._user_repo.get_by_email(email)
        if not user or not self._auth_service.verify_password(password, user.hashed_password):
            raise InvalidCredentials("Invalid email or password")
        if not user.is_active:
            raise UserIsBanned("Your account has been banned")

        access_token = self._auth_service.create_access_token(user.id, user.role)
        refresh_token = self._auth_service.create_refresh_token(user.id)
        return LoginOutput(access_token=access_token, refresh_token=refresh_token)
