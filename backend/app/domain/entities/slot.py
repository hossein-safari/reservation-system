from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.errors.conflict import ConflictError
from app.domain.errors.validation import ValidationError
from app.domain.validation import validate_amount


@dataclass(eq=False)
class Slot:
    resource_id: UUID
    starts_at: datetime
    ends_at: datetime
    price_irr: int
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.starts_at.utcoffset() is None or self.ends_at.utcoffset() is None:
            raise ValidationError("timezone_required", "Timezone-aware dates are required.")
        if self.ends_at <= self.starts_at:
            raise ValidationError("invalid_interval", "End must be after start.")
        validate_amount(self.price_irr)
        self.starts_at = self.starts_at.astimezone(UTC)
        self.ends_at = self.ends_at.astimezone(UTC)

    def ensure_future(self, now: datetime) -> None:
        if self.starts_at <= now:
            raise ValidationError("past_slot", "A slot must start in the future.")

    def ensure_bookable(self, now: datetime) -> None:
        if self.starts_at <= now:
            raise ConflictError("slot_unavailable", "This slot is no longer available.")
