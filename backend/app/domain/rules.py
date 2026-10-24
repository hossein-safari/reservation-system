from datetime import UTC, datetime

from app.domain.errors import DomainError


def validate_slot(starts_at: datetime, ends_at: datetime, price_irr: int) -> None:
    if starts_at.tzinfo is None or ends_at.tzinfo is None:
        raise DomainError("timezone_required", "Timezone-aware dates are required.", 422)
    if ends_at <= starts_at:
        raise DomainError("invalid_interval", "End must be after start.", 422)
    if starts_at <= datetime.now(UTC):
        raise DomainError("past_slot", "A slot must start in the future.", 422)
    if price_irr <= 0:
        raise DomainError("invalid_price", "Price must be a positive integer in IRR.", 422)
