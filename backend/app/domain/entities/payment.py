from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.entities.reservation import Reservation
from app.domain.errors.conflict import ConflictError
from app.domain.time import utcnow
from app.domain.validation import validate_amount


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"


@dataclass(eq=False)
class Payment:
    reservation_id: UUID
    amount_irr: int
    provider_reference: str
    status: PaymentStatus = PaymentStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        validate_amount(self.amount_irr)

    def ensure_matches(self, reservation: Reservation) -> None:
        if self.reservation_id != reservation.id or self.amount_irr != reservation.amount_irr:
            raise ConflictError("verification_failed", "Payment does not match the reservation.")

    def ensure_pending(self) -> None:
        if self.status != PaymentStatus.PENDING:
            raise ConflictError("payment_inconsistent", "Payment state cannot be completed again.")

    def succeed(self) -> None:
        self.ensure_pending()
        self.status = PaymentStatus.SUCCEEDED
