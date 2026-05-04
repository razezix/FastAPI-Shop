from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime, timezone

from src.core.exceptions import UserAlreadyExists
from src.domain.services.auth_service import AbstractAuthService
from src.domain.services.email_service import AbstractEmailService
from src.domain.users.entities import User
from src.domain.users.enums import UserRole
from src.domain.users.repositories import AbstractUserRepository


@dataclass
class RegisterInput:
    email: str
    password: str
    first_name: str
    last_name: str


@dataclass
class RegisterOutput:
    user_id: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterUseCase:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        auth_service: AbstractAuthService,
        email_service: AbstractEmailService,
    ) -> None:
        self._user_repo = user_repo
        self._auth_service = auth_service
        self._email_service = email_service

    async def execute(self, input: RegisterInput) -> RegisterOutput:
        existing = await self._user_repo.get_by_email(input.email)
        if existing:
            raise UserAlreadyExists(f"Email {input.email} is already registered")

        now = datetime.now(timezone.utc)
        user = User(
            id=uuid4(),
            email=input.email.lower().strip(),
            hashed_password=self._auth_service.hash_password(input.password),
            first_name=input.first_name,
            last_name=input.last_name,
            role=UserRole.USER,
            is_active=True,
            is_verified=False,
            created_at=now,
            updated_at=now,
        )
        created = await self._user_repo.create(user)

        access_token = self._auth_service.create_access_token(created.id, created.role)
        refresh_token = self._auth_service.create_refresh_token(created.id)

        try:
            await self._email_service.send_welcome_email(created.email, created.first_name)
        except Exception:
            pass

        return RegisterOutput(
            user_id=str(created.id),
            access_token=access_token,
            refresh_token=refresh_token,
        )
