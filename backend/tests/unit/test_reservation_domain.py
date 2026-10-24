from datetime import timedelta
from uuid import uuid4

import pytest

from app.domain.entities.reservation import Reservation, ReservationStatus
from app.domain.entities.slot import Slot
from app.domain.entities.user import Role, User
from app.domain.errors.authorization import AuthorizationError
from app.domain.errors.conflict import ConflictError
from tests.fakes.clock import FrozenClock


def test_paid_reservation_cannot_be_cancelled(slot: Slot, clock: FrozenClock) -> None:
    reservation = Reservation.place(uuid4(), slot, clock.now())
    reservation.confirm(clock.now())
    with pytest.raises(ConflictError, match="refund workflow"):
        reservation.cancel()
    assert reservation.status == ReservationStatus.CONFIRMED


def test_cancelled_reservation_cannot_be_confirmed(slot: Slot, clock: FrozenClock) -> None:
    reservation = Reservation.place(uuid4(), slot, clock.now())
    reservation.cancel()
    reservation.cancel()
    with pytest.raises(ConflictError, match="cannot be paid"):
        reservation.confirm(clock.now())
    assert reservation.status == ReservationStatus.CANCELLED


def test_expiration_rule_uses_explicit_time(slot: Slot, clock: FrozenClock) -> None:
    reservation = Reservation.place(uuid4(), slot, clock.now())
    with pytest.raises(ConflictError, match="cannot be paid"):
        reservation.ensure_payable(clock.now() + timedelta(days=2))


def test_role_policy_belongs_to_user() -> None:
    customer = User("Customer", "CUSTOMER@EXAMPLE.COM", "hashed")
    assert customer.email == "customer@example.com"
    with pytest.raises(AuthorizationError):
        customer.require_admin()
    User("Admin", "admin@example.com", "hashed", Role.ADMIN).require_admin()
