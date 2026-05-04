from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import EntityNotFound
from src.domain.users.entities import User
from src.domain.users.enums import UserRole
from src.domain.users.repositories import AbstractUserRepository
from src.infrastructure.database.models.user import UserModel


def _to_entity(m: UserModel) -> User:
    return User(
        id=UUID(m.id),
        email=m.email,
        hashed_password=m.hashed_password,
        first_name=m.first_name,
        last_name=m.last_name,
        role=UserRole(m.role),
        is_active=m.is_active,
        is_verified=m.is_verified,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        model = UserModel(
            id=str(user.id),
            email=user.email,
            hashed_password=user.hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == str(user_id)))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update(self, user: User) -> User:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == str(user.id))
            .values(
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_verified=user.is_verified,
                updated_at=datetime.now(timezone.utc),
            )
        )
        result = await self._session.execute(select(UserModel).where(UserModel.id == str(user.id)))
        return _to_entity(result.scalar_one())

    async def list_all(self, skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
        count_result = await self._session.execute(select(func.count()).select_from(UserModel))
        total = count_result.scalar_one()
        result = await self._session.execute(select(UserModel).offset(skip).limit(limit))
        return [_to_entity(m) for m in result.scalars()], total

    async def change_role(self, user_id: UUID, role: UserRole) -> User:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == str(user_id))
            .values(role=role.value, updated_at=datetime.now(timezone.utc))
        )
        result = await self._session.execute(select(UserModel).where(UserModel.id == str(user_id)))
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFound(f"User {user_id} not found")
        return _to_entity(model)

    async def set_active(self, user_id: UUID, is_active: bool) -> User:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == str(user_id))
            .values(is_active=is_active, updated_at=datetime.now(timezone.utc))
        )
        result = await self._session.execute(select(UserModel).where(UserModel.id == str(user_id)))
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFound(f"User {user_id} not found")
        return _to_entity(model)
