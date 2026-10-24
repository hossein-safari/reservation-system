from uuid import UUID

from app.domain.entities.payment import Payment


class MemoryPayments:
    def __init__(self) -> None:
        self.records: dict[UUID, Payment] = {}

    def get(self, payment_id: UUID) -> Payment | None:
        return self.records.get(payment_id)

    def for_reservation(self, reservation_id: UUID) -> Payment | None:
        return next((p for p in self.records.values() if p.reservation_id == reservation_id), None)

    def add(self, payment: Payment) -> None:
        self.records[payment.id] = payment
