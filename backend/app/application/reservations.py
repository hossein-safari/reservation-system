from uuid import UUID

from app.application.ports import BookingRepository, UnitOfWork
from app.domain.entities import Reservation, ReservationStatus, utcnow
from app.domain.errors import DomainError, not_found


class ReservationService:
    def __init__(self, bookings: BookingRepository, uow: UnitOfWork) -> None:
        self.bookings = bookings
        self.uow = uow

    def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Reservation]:
        return self.bookings.list_owned(user_id, limit, offset)

    def create(self, user_id: UUID, slot_id: UUID) -> Reservation:
        slot = self.bookings.slot(slot_id)
        if not slot:
            raise not_found()
        if slot.starts_at <= utcnow() or self.bookings.active_for_slot(slot_id):
            raise DomainError("slot_unavailable", "This slot is no longer available.")
        reservation = Reservation(user_id, slot.id, slot.price_irr)
        reservation.slot = slot
        self.bookings.add(reservation)
        self.uow.commit()
        return reservation

    def cancel(self, user_id: UUID, reservation_id: UUID) -> Reservation:
        reservation = self.bookings.owned(reservation_id, user_id)
        if not reservation:
            raise not_found()
        if reservation.status == ReservationStatus.CONFIRMED:
            raise DomainError("refund_required", "Paid reservations require a refund workflow.")
        reservation.status = ReservationStatus.CANCELLED
        self.uow.commit()
        return reservation
