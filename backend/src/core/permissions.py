from src.domain.users.entities import User
from src.domain.users.enums import UserRole


def can_manage_products(user: User) -> bool:
    return user.role in (UserRole.MANAGER, UserRole.ADMIN)


def can_manage_users(user: User) -> bool:
    return user.role == UserRole.ADMIN


def can_view_analytics(user: User) -> bool:
    return user.role == UserRole.ADMIN


def can_manage_orders(user: User) -> bool:
    return user.role in (UserRole.MANAGER, UserRole.ADMIN)


def can_manage_discounts(user: User) -> bool:
    return user.role in (UserRole.MANAGER, UserRole.ADMIN)


def is_resource_owner(user: User, owner_id) -> bool:
    return user.id == owner_id


def can_access_resource(user: User, owner_id) -> bool:
    return is_resource_owner(user, owner_id) or user.role == UserRole.ADMIN
