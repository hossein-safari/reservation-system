from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.entities.slot import Slot


class SlotRepository(Protocol):
    def get(self, slot_id: UUID) -> Slot | None: ...
    def add(self, slot: Slot) -> None: ...
    def overlaps(self, resource_id: UUID, starts_at: datetime, ends_at: datetime) -> bool: ...
    def list(
        self, resource_id: UUID | None, available_only: bool, limit: int, offset: int
    ) -> list[Slot]: ...
