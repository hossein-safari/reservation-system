from app.domain.errors.base import DomainError


class ConflictError(DomainError):
    """Conflict failure independent of transport."""
