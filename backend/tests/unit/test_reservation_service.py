from uuid import uuid4

import pytest

from app.application.services.reservations import ReservationService
from app.domain.entities.slot import Slot
from app.domain.errors.conflict import ConflictError
from tests.fakes.clock import FrozenClock
from tests.fakes.reservations import MemoryReservations
from tests.fakes.slots import MemorySlots
from tests.fakes.unit_of_work import MemoryUnitOfWork


def test_price_snapshot_and_duplicate_failure_are_atomic(slot: Slot, clock: FrozenClock) -> None:
    bookings = MemoryReservations()
    slots = MemorySlots(clock, bookings)
    slots.add(slot)
    uow = MemoryUnitOfWork()
    service = ReservationService(bookings, slots, uow, clock)
    record = service.create(uuid4(), slot.id)
    assert record.amount_irr == slot.price_irr
    assert uow.commits == 1
    with pytest.raises(ConflictError):
        service.create(uuid4(), slot.id)
    assert uow.commits == 1
    assert uow.rollbacks == 1
    assert len(bookings.records) == 1
