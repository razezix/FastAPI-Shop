from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import get_settings
from src.core.exceptions import InvalidCredentials
from src.domain.services.auth_service import AbstractAuthService
from src.domain.users.enums import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTAuthService(AbstractAuthService):
    def __init__(self) -> None:
        self._settings = get_settings()

    def hash_password(self, plain: str) -> str:
        return pwd_context.hash(plain)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def create_access_token(self, user_id: UUID, role: UserRole) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": str(user_id),
            "role": role.value,
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self._settings.JWT_SECRET_KEY, algorithm=self._settings.JWT_ALGORITHM)

    def create_refresh_token(self, user_id: UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            days=self._settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self._settings.JWT_SECRET_KEY, algorithm=self._settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._settings.JWT_SECRET_KEY, algorithms=[self._settings.JWT_ALGORITHM])
            return payload
        except JWTError as e:
            raise InvalidCredentials(f"Invalid token: {e}") from e
