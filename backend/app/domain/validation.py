from app.domain.errors.validation import ValidationError

MAX_AMOUNT_IRR = 1_000_000_000_000


def validate_amount(amount: int) -> None:
    if isinstance(amount, bool) or not isinstance(amount, int) or not 0 < amount <= MAX_AMOUNT_IRR:
        raise ValidationError("invalid_price", "Amount must be a positive integer in IRR.")


def validate_name(value: str) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > 120:
        raise ValidationError("invalid_name", "Name must contain between 1 and 120 characters.")
    return normalized
