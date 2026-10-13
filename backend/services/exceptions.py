from abc import ABC


class DomainError(Exception, ABC):
    """Base for all domain-level errors"""


class UrlNotFoundError(DomainError):
    def __init__(self, url_id: str) -> None:
        self.url_id = url_id
        super().__init__(f"URL not found: {url_id}")


class AccessDeniedError(DomainError):
    def __init__(self) -> None:
        super().__init__('Access denied')


class UserNotFoundError(DomainError):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")


class SessionNotFoundError(DomainError):
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")
