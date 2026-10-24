from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.entities.slot import Slot
from app.domain.errors.conflict import ConflictError
from app.domain.time import utcnow
from app.domain.validation import validate_amount


class ReservationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass(eq=False)
class Reservation:
    user_id: UUID
    slot_id: UUID
    amount_irr: int
    status: ReservationStatus = ReservationStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utcnow)
    slot: Slot | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        validate_amount(self.amount_irr)

    @classmethod
    def place(cls, user_id: UUID, slot: Slot, now: datetime) -> "Reservation":
        slot.ensure_bookable(now)
        reservation = cls(user_id, slot.id, slot.price_irr, created_at=now)
        reservation.slot = slot
        return reservation

    def ensure_payable(self, now: datetime) -> None:
        if self.status != ReservationStatus.PENDING or not self.slot or self.slot.starts_at <= now:
            raise ConflictError("reservation_not_payable", "This reservation cannot be paid.")

    def cancel(self) -> None:
        if self.status == ReservationStatus.CONFIRMED:
            raise ConflictError("refund_required", "Paid reservations require a refund workflow.")
        self.status = ReservationStatus.CANCELLED

    def confirm(self, now: datetime) -> None:
        self.ensure_payable(now)
        self.status = ReservationStatus.CONFIRMED
