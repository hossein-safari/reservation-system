from uuid import UUID

from app.application.ports import BookingRepository, PaymentGateway, PaymentRepository, UnitOfWork
from app.domain.entities import (
    Payment,
    PaymentStatus,
    Reservation,
    ReservationStatus,
    Transaction,
    utcnow,
)
from app.domain.errors import DomainError, not_found


class PaymentService:
    def __init__(
        self,
        bookings: BookingRepository,
        payments: PaymentRepository,
        gateway: PaymentGateway,
        uow: UnitOfWork,
    ) -> None:
        self.bookings = bookings
        self.payments = payments
        self.gateway = gateway
        self.uow = uow

    def _pending(self, reservation: Reservation) -> None:
        slot = self.bookings.slot(reservation.slot_id)
        if (
            reservation.status != ReservationStatus.PENDING
            or not slot
            or slot.starts_at <= utcnow()
        ):
            raise DomainError("reservation_not_payable", "This reservation cannot be paid.")

    def create(self, user_id: UUID, reservation_id: UUID) -> Payment:
        reservation = self.bookings.owned(reservation_id, user_id)
        if not reservation:
            raise not_found()
        existing = self.payments.for_reservation(reservation_id)
        if existing and reservation.status != ReservationStatus.CANCELLED:
            return existing
        self._pending(reservation)
        reference = self.gateway.create(reservation.id, reservation.amount_irr)
        payment = Payment(reservation.id, reservation.amount_irr, reference)
        self.payments.add(payment)
        self.uow.commit()
        return payment

    def verify(self, user_id: UUID, payment_id: UUID) -> Transaction:
        # Read only to discover the reservation. Always acquire reservation before payment lock.
        payment = self.payments.get(payment_id)
        if not payment:
            raise not_found()
        reservation = self.bookings.owned(payment.reservation_id, user_id)
        if not reservation:
            raise not_found()
        payment = self.payments.for_reservation(reservation.id)
        if payment is None:
            raise not_found()
        existing = self.payments.transaction(payment.id)
        if existing and payment.status == PaymentStatus.SUCCEEDED:
            return existing
        self._pending(reservation)
        reference = self.gateway.verify(payment.provider_reference, payment.amount_irr)
        transaction = Transaction(payment.id, reference, payment.amount_irr)
        payment.status = PaymentStatus.SUCCEEDED
        reservation.status = ReservationStatus.CONFIRMED
        self.payments.add_transaction(transaction)
        self.uow.commit()
        return transaction

    def transactions(self, user_id: UUID, limit: int, offset: int) -> list[Transaction]:
        return self.payments.list_transactions(user_id, limit, offset)
