from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4

import pytest

from app.application.services.payments import PaymentService
from app.domain.entities.payment import PaymentStatus
from app.domain.entities.reservation import Reservation, ReservationStatus
from app.domain.entities.slot import Slot
from app.domain.errors.conflict import ConflictError
from app.domain.errors.not_found import NotFoundError
from tests.fakes.clock import FrozenClock
from tests.fakes.gateway import FakeGateway
from tests.fakes.payments import MemoryPayments
from tests.fakes.reservations import MemoryReservations
from tests.fakes.transactions import MemoryTransactions
from tests.fakes.unit_of_work import MemoryUnitOfWork


@dataclass
class PaymentCase:
    service: PaymentService
    reservation: Reservation
    payments: MemoryPayments
    transactions: MemoryTransactions
    gateway: FakeGateway
    uow: MemoryUnitOfWork


@pytest.fixture
def case(slot: Slot, clock: FrozenClock) -> PaymentCase:
    bookings, payments = MemoryReservations(), MemoryPayments()
    transactions = MemoryTransactions(payments, bookings)
    uow, gateway = MemoryUnitOfWork(), FakeGateway()
    reservation = Reservation.place(uuid4(), slot, clock.now())
    bookings.add(reservation)
    service = PaymentService(bookings, payments, transactions, gateway, uow, clock)
    return PaymentCase(service, reservation, payments, transactions, gateway, uow)


def test_gateway_can_be_replaced_without_service_changes(case: PaymentCase) -> None:
    user_id = case.reservation.user_id
    payment = case.service.create(user_id, case.reservation.id)
    assert case.service.create(user_id, case.reservation.id).id == payment.id
    first = case.service.verify(user_id, payment.id)
    assert case.service.verify(user_id, payment.id).id == first.id
    assert case.gateway.calls == 1
    assert len(case.transactions.records) == 1
    assert case.reservation.status == ReservationStatus.CONFIRMED
    assert payment.status == PaymentStatus.SUCCEEDED


def test_gateway_failure_does_not_change_domain_state(case: PaymentCase) -> None:
    payment = case.service.create(case.reservation.user_id, case.reservation.id)
    case.gateway.fail = True
    with pytest.raises(ConflictError):
        case.service.verify(case.reservation.user_id, payment.id)
    assert case.reservation.status == ReservationStatus.PENDING
    assert payment.status == PaymentStatus.PENDING
    assert not case.transactions.records
    assert case.uow.rollbacks == 1


def test_mismatched_amount_never_reaches_gateway(case: PaymentCase) -> None:
    payment = case.service.create(case.reservation.user_id, case.reservation.id)
    payment.amount_irr += 1
    with pytest.raises(ConflictError, match="does not match"):
        case.service.verify(case.reservation.user_id, payment.id)
    assert case.gateway.calls == 0
    assert not case.transactions.records


def test_owned_payment_cannot_be_verified_by_another_customer(case: PaymentCase) -> None:
    payment = case.service.create(case.reservation.user_id, case.reservation.id)
    with pytest.raises(NotFoundError):
        case.service.verify(uuid4(), payment.id)
    assert case.gateway.calls == 0


def test_existing_pending_intent_cannot_bypass_start_time(
    case: PaymentCase, clock: FrozenClock
) -> None:
    case.service.create(case.reservation.user_id, case.reservation.id)
    clock.value += timedelta(days=2)
    with pytest.raises(ConflictError, match="cannot be paid"):
        case.service.create(case.reservation.user_id, case.reservation.id)


def test_paid_receipt_stays_idempotent_after_start_time(
    case: PaymentCase, clock: FrozenClock
) -> None:
    payment = case.service.create(case.reservation.user_id, case.reservation.id)
    receipt = case.service.verify(case.reservation.user_id, payment.id)
    clock.value += timedelta(days=2)
    assert case.service.verify(case.reservation.user_id, payment.id).id == receipt.id
    assert case.gateway.calls == 1
