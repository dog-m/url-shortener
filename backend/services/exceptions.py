from abc import ABC
from uuid import UUID


class DomainError(Exception, ABC):
    """Base for all domain-level errors"""


class EntityNotFoundError(DomainError, ABC):
    """Base for all "item is missing" errors"""


class UrlNotFoundError(EntityNotFoundError):
    def __init__(self, url_id: str) -> None:
        self.url_id = url_id
        super().__init__(f"URL not found: {url_id}")


class UserNotFoundError(EntityNotFoundError):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")


class AccessControlError(DomainError, ABC):
    """Base for all access- and security-related errors"""


class AccessDeniedError(AccessControlError):
    def __init__(self) -> None:
        super().__init__('Access denied')


class InsufficientPrivilegesError(AccessControlError):
    def __init__(self) -> None:
        super().__init__('Insufficient privileges')


class ConcurrentUpdateError(DomainError):
    def __init__(self) -> None:
        super().__init__('Concurrent update or stale data')

