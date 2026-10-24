from datetime import datetime
from uuid import UUID

from app.application.ports.clock import Clock
from app.application.ports.resource_repository import ResourceRepository
from app.application.ports.slot_repository import SlotRepository
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.slot import Slot
from app.domain.errors.conflict import ConflictError
from app.domain.errors.not_found import NotFoundError


class SlotService:
    def __init__(
        self, resources: ResourceRepository, slots: SlotRepository, uow: UnitOfWork, clock: Clock
    ) -> None:
        self._resources = resources
        self._slots = slots
        self._uow = uow
        self._clock = clock

    def list(
        self, resource_id: UUID | None, available_only: bool, limit: int, offset: int
    ) -> list[Slot]:
        return self._slots.list(resource_id, available_only, limit, offset)

    def create(
        self, resource_id: UUID, starts_at: datetime, ends_at: datetime, price_irr: int
    ) -> Slot:
        with self._uow.transaction():
            slot = Slot(resource_id, starts_at, ends_at, price_irr)
            slot.ensure_future(self._clock.now())
            if not self._resources.get_for_update(resource_id):
                raise NotFoundError()
            if self._slots.overlaps(resource_id, slot.starts_at, slot.ends_at):
                raise ConflictError("overlapping_slot", "Slots for a resource cannot overlap.")
            self._slots.add(slot)
        return slot
