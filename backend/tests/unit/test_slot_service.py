import pytest

from app.application.services.slots import SlotService
from app.domain.entities.resource import Resource
from app.domain.entities.slot import Slot
from app.domain.errors.conflict import ConflictError
from tests.fakes.clock import FrozenClock
from tests.fakes.reservations import MemoryReservations
from tests.fakes.resources import MemoryResources
from tests.fakes.slots import MemorySlots
from tests.fakes.unit_of_work import MemoryUnitOfWork


def test_overlap_checks_are_serialized_by_resource_contract(slot: Slot, clock: FrozenClock) -> None:
    resources = MemoryResources()
    resources.add(Resource("Court", id=slot.resource_id))
    slots = MemorySlots(clock, MemoryReservations())
    slots.add(slot)
    uow = MemoryUnitOfWork()
    service = SlotService(resources, slots, uow, clock)
    with pytest.raises(ConflictError, match="overlap"):
        service.create(slot.resource_id, slot.starts_at, slot.ends_at, 1000)
    assert resources.locked == [slot.resource_id]
    assert uow.rollbacks == 1
    assert uow.commits == 0
