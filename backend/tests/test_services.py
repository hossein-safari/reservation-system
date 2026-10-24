from datetime import timedelta
from uuid import uuid4

import pytest

from app.application.reservations import ReservationService
from app.config import Settings
from app.domain.entities import Reservation, Slot, utcnow
from app.domain.errors import DomainError
from app.infrastructure.gateway import DevelopmentGateway


class MemoryBookings:
    def __init__(self, slot: Slot) -> None:
        self.value = slot
        self.records: list[Reservation] = []

    def slot(self, slot_id: object) -> Slot:
        return self.value

    def active_for_slot(self, slot_id: object) -> bool:
        return bool(self.records)

    def add(self, reservation: Reservation) -> None:
        self.records.append(reservation)

    def owned(self, reservation_id: object, user_id: object) -> Reservation | None:
        return next(
            (r for r in self.records if r.id == reservation_id and r.user_id == user_id), None
        )

    def list_owned(self, user_id: object, limit: int, offset: int) -> list[Reservation]:
        return [r for r in self.records if r.user_id == user_id][offset : offset + limit]


class MemoryUnitOfWork:
    committed = False

    def commit(self) -> None:
        self.committed = True


def test_reservation_service_uses_injected_repository_and_server_price() -> None:
    slot = Slot(uuid4(), utcnow() + timedelta(days=1), utcnow() + timedelta(days=2), 850000)
    bookings = MemoryBookings(slot)
    uow = MemoryUnitOfWork()
    service = ReservationService(bookings, uow)
    record = service.create(uuid4(), slot.id)
    assert record.amount_irr == 850000
    assert uow.committed
    with pytest.raises(DomainError, match="no longer available"):
        service.create(uuid4(), slot.id)


def test_production_disables_simulator_and_requires_secret() -> None:
    with pytest.raises(ValueError, match="APP_SECRET_KEY"):
        Settings(app_env="production")
    with pytest.raises(DomainError, match="production gateway"):
        DevelopmentGateway("production").create(uuid4(), 1000)
