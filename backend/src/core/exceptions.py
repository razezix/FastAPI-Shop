class DomainException(Exception):
    pass


class EntityNotFound(DomainException):
    pass


class AccessDenied(DomainException):
    pass


class InvalidCredentials(DomainException):
    pass


class UserAlreadyExists(DomainException):
    pass


class UserIsBanned(DomainException):
    pass


class InsufficientStock(DomainException):
    pass


class ProductIsArchived(DomainException):
    pass


class InvalidDiscountCode(DomainException):
    pass


class DiscountExpired(DomainException):
    pass


class DiscountUsageLimitReached(DomainException):
    pass


class OrderCannotBeCancelled(DomainException):
    pass


class InvalidOrderStatusTransition(DomainException):
    pass


class PaymentFailed(DomainException):
    pass


class DuplicateReview(DomainException):
    pass


class InvalidRating(DomainException):
    pass


class CartIsEmpty(DomainException):
    pass
