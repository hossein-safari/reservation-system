from uuid import UUID

from app.application.ports.clock import Clock
from app.application.ports.reservation_repository import ReservationRepository
from app.application.ports.slot_repository import SlotRepository
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.reservation import Reservation
from app.domain.errors.conflict import ConflictError
from app.domain.errors.not_found import NotFoundError


class ReservationService:
    def __init__(
        self, bookings: ReservationRepository, slots: SlotRepository, uow: UnitOfWork, clock: Clock
    ) -> None:
        self._bookings = bookings
        self._slots = slots
        self._uow = uow
        self._clock = clock

    def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Reservation]:
        return self._bookings.list_owned(user_id, limit, offset)

    def create(self, user_id: UUID, slot_id: UUID) -> Reservation:
        with self._uow.transaction():
            slot = self._slots.get(slot_id)
            if not slot:
                raise NotFoundError()
            if self._bookings.active_for_slot(slot_id):
                raise ConflictError("slot_unavailable", "This slot is no longer available.")
            reservation = Reservation.place(user_id, slot, self._clock.now())
            self._bookings.add(reservation)
        return reservation

    def cancel(self, user_id: UUID, reservation_id: UUID) -> Reservation:
        with self._uow.transaction():
            reservation = self._bookings.owned_for_update(reservation_id, user_id)
            if not reservation:
                raise NotFoundError()
            reservation.cancel()
        return reservation
