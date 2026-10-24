from uuid import UUID

from app.application.ports.clock import Clock
from app.application.ports.payment_gateway import PaymentGateway
from app.application.ports.payment_repository import PaymentRepository
from app.application.ports.reservation_repository import ReservationRepository
from app.application.ports.transaction_repository import TransactionRepository
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.payment import Payment, PaymentStatus
from app.domain.entities.reservation import ReservationStatus
from app.domain.entities.transaction import Transaction
from app.domain.errors.conflict import ConflictError
from app.domain.errors.not_found import NotFoundError


class PaymentService:
    def __init__(
        self,
        bookings: ReservationRepository,
        payments: PaymentRepository,
        transactions: TransactionRepository,
        gateway: PaymentGateway,
        uow: UnitOfWork,
        clock: Clock,
    ) -> None:
        self._bookings = bookings
        self._payments = payments
        self._transactions = transactions
        self._gateway = gateway
        self._uow = uow
        self._clock = clock

    def create(self, user_id: UUID, reservation_id: UUID) -> Payment:
        with self._uow.transaction():
            reservation = self._bookings.owned_for_update(reservation_id, user_id)
            if not reservation:
                raise NotFoundError()
            existing = self._payments.for_reservation(reservation.id)
            if existing:
                existing.ensure_matches(reservation)
                if existing.status == PaymentStatus.SUCCEEDED:
                    if reservation.status != ReservationStatus.CONFIRMED:
                        raise ConflictError(
                            "payment_inconsistent", "Payment and reservation disagree."
                        )
                    return existing
            reservation.ensure_payable(self._clock.now())
            if existing:
                return existing
            reference = self._gateway.create(reservation.id, reservation.amount_irr)
            payment = Payment(
                reservation.id, reservation.amount_irr, reference, created_at=self._clock.now()
            )
            self._payments.add(payment)
        return payment

    def verify(self, user_id: UUID, payment_id: UUID) -> Transaction:
        with self._uow.transaction():
            # Discover ownership, then always lock reservation before payment.
            payment = self._payments.get(payment_id)
            if not payment:
                raise NotFoundError()
            reservation = self._bookings.owned_for_update(payment.reservation_id, user_id)
            if not reservation:
                raise NotFoundError()
            payment = self._payments.for_reservation(reservation.id)
            if payment is None:
                raise NotFoundError()
            payment.ensure_matches(reservation)
            existing = self._transactions.for_payment(payment.id)
            if existing:
                if (
                    payment.status != PaymentStatus.SUCCEEDED
                    or reservation.status != ReservationStatus.CONFIRMED
                ):
                    raise ConflictError("payment_inconsistent", "Payment and reservation disagree.")
                return existing
            payment.ensure_pending()
            now = self._clock.now()
            reservation.ensure_payable(now)
            reference = self._gateway.verify(payment.provider_reference, payment.amount_irr)
            transaction = Transaction(payment.id, reference, payment.amount_irr, created_at=now)
            payment.succeed()
            reservation.confirm(now)
            self._transactions.add(transaction)
        return transaction
