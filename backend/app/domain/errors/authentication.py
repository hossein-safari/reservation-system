from app.domain.errors.base import DomainError


class AuthenticationError(DomainError):
    """Authentication failure independent of transport."""
