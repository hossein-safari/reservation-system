from datetime import datetime
from uuid import UUID

from app.application.ports.clock import Clock
from app.domain.entities.slot import Slot
from tests.fakes.reservations import MemoryReservations


class MemorySlots:
    def __init__(self, clock: Clock, bookings: MemoryReservations) -> None:
        self.records: dict[UUID, Slot] = {}
        self.clock = clock
        self.bookings = bookings

    def get(self, slot_id: UUID) -> Slot | None:
        return self.records.get(slot_id)

    def add(self, slot: Slot) -> None:
        self.records[slot.id] = slot

    def overlaps(self, resource_id: UUID, starts_at: datetime, ends_at: datetime) -> bool:
        return any(
            slot.resource_id == resource_id
            and slot.starts_at < ends_at
            and slot.ends_at > starts_at
            for slot in self.records.values()
        )

    def list(
        self, resource_id: UUID | None, available_only: bool, limit: int, offset: int
    ) -> list[Slot]:
        matches = [
            slot
            for slot in self.records.values()
            if (resource_id is None or slot.resource_id == resource_id)
            and (
                not available_only
                or (
                    slot.starts_at > self.clock.now() and not self.bookings.active_for_slot(slot.id)
                )
            )
        ]
        return sorted(matches, key=lambda slot: slot.starts_at)[offset : offset + limit]
