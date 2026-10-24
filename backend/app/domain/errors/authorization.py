from app.domain.errors.base import DomainError


class AuthorizationError(DomainError):
    """Authorization failure independent of transport."""
