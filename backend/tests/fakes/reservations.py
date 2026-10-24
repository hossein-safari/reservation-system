from uuid import UUID

from app.domain.entities.reservation import Reservation, ReservationStatus


class MemoryReservations:
    def __init__(self) -> None:
        self.records: dict[UUID, Reservation] = {}

    def active_for_slot(self, slot_id: UUID) -> bool:
        return any(
            record.slot_id == slot_id and record.status != ReservationStatus.CANCELLED
            for record in self.records.values()
        )

    def add(self, reservation: Reservation) -> None:
        self.records[reservation.id] = reservation

    def owned_for_update(self, reservation_id: UUID, user_id: UUID) -> Reservation | None:
        reservation = self.records.get(reservation_id)
        return reservation if reservation and reservation.user_id == user_id else None

    def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Reservation]:
        return sorted(
            (r for r in self.records.values() if r.user_id == user_id),
            key=lambda r: r.created_at,
            reverse=True,
        )[offset : offset + limit]
