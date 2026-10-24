from app.domain.errors.base import DomainError


class UnavailableError(DomainError):
    """Unavailable failure independent of transport."""
