from uuid import UUID

from app.domain.entities.transaction import Transaction
from app.domain.errors.conflict import ConflictError
from tests.fakes.payments import MemoryPayments
from tests.fakes.reservations import MemoryReservations


class MemoryTransactions:
    def __init__(self, payments: MemoryPayments, bookings: MemoryReservations) -> None:
        self.records: dict[UUID, Transaction] = {}
        self._payments = payments
        self._bookings = bookings

    def for_payment(self, payment_id: UUID) -> Transaction | None:
        return next((t for t in self.records.values() if t.payment_id == payment_id), None)

    def add(self, transaction: Transaction) -> None:
        if self.for_payment(transaction.payment_id):
            raise ConflictError("conflict", "Only one receipt per payment is permitted.")
        self.records[transaction.id] = transaction

    def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Transaction]:
        payment_ids = {
            payment.id
            for payment in self._payments.records.values()
            if (booking := self._bookings.records.get(payment.reservation_id))
            and booking.user_id == user_id
        }
        matches = [t for t in self.records.values() if t.payment_id in payment_ids]
        return sorted(matches, key=lambda t: t.created_at, reverse=True)[offset : offset + limit]
