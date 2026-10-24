from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.application.ports.reservation_repository import ReservationRepository
from app.application.ports.resource_repository import ResourceRepository
from app.application.ports.slot_repository import SlotRepository
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.user_repository import UserRepository
from app.domain.entities.reservation import Reservation
from app.domain.entities.resource import Resource
from app.domain.entities.slot import Slot
from app.domain.entities.user import User
from app.infrastructure.persistence.repositories.reservation import SqlReservationRepository
from app.infrastructure.persistence.repositories.resource import SqlResourceRepository
from app.infrastructure.persistence.repositories.slot import SqlSlotRepository
from app.infrastructure.persistence.repositories.user import SqlUserRepository
from app.infrastructure.persistence.unit_of_work import SqlUnitOfWork
from tests.fakes.clock import FrozenClock
from tests.fakes.reservations import MemoryReservations
from tests.fakes.resources import MemoryResources
from tests.fakes.slots import MemorySlots
from tests.fakes.unit_of_work import MemoryUnitOfWork
from tests.fakes.users import MemoryUsers


@pytest.mark.parametrize("implementation", ["sql", "memory"])
def test_same_repository_contract_with_both_adapters(
    client: TestClient, implementation: str
) -> None:
    database = client.app.state.container.database
    clock = FrozenClock(datetime(2035, 1, 1, tzinfo=UTC))
    with database.session() as session:
        users: UserRepository
        resources: ResourceRepository
        bookings: ReservationRepository
        slots: SlotRepository
        uow: UnitOfWork
        if implementation == "sql":
            users, resources = SqlUserRepository(session), SqlResourceRepository(session)
            bookings, slots = SqlReservationRepository(session), SqlSlotRepository(session, clock)
            uow = SqlUnitOfWork(session)
        else:
            memory_bookings = MemoryReservations()
            users, resources = MemoryUsers(), MemoryResources()
            bookings, slots = memory_bookings, MemorySlots(clock, memory_bookings)
            uow = MemoryUnitOfWork()
        with uow.transaction():
            user = User("Contract customer", "contract@example.com", "hashed")
            resource = Resource("Contract room")
            slot = Slot(
                resource.id,
                clock.now() + timedelta(days=1),
                clock.now() + timedelta(days=1, hours=1),
                1000,
            )
            users.add(user)
            resources.add(resource)
            slots.add(slot)
            assert users.by_id(user.id) is user
            assert users.by_email("contract@example.com") is user
            assert users.by_id(uuid4()) is None
            assert resources.get_for_update(resource.id) is resource
            assert slots.get(slot.id) is slot
            assert slots.list(resource.id, True, 10, 0) == [slot]
            reservation = Reservation.place(user.id, slot, clock.now())
            bookings.add(reservation)
            assert bookings.owned_for_update(reservation.id, user.id) is reservation
            assert bookings.owned_for_update(reservation.id, uuid4()) is None
            assert bookings.list_owned(user.id, 10, 0) == [reservation]
            assert slots.list(resource.id, True, 10, 0) == []
            reservation.cancel()
            assert slots.list(resource.id, True, 10, 0) == [slot]
