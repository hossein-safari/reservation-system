from app.domain.errors.base import DomainError


class ValidationError(DomainError):
    """Validation failure independent of transport."""
