from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.application.ports.clock import Clock
from app.domain.entities.reservation import ReservationStatus
from app.domain.entities.slot import Slot
from app.infrastructure.persistence.models.reservation import reservations
from app.infrastructure.persistence.models.slot import slots


class SqlSlotRepository:
    def __init__(self, session: Session, clock: Clock) -> None:
        self.session = session
        self.clock = clock

    def get(self, slot_id: UUID) -> Slot | None:
        return self.session.get(Slot, slot_id)

    def add(self, slot: Slot) -> None:
        self.session.add(slot)
        self.session.flush()

    def overlaps(self, resource_id: UUID, starts_at: datetime, ends_at: datetime) -> bool:
        return bool(
            self.session.scalar(
                select(
                    exists().where(
                        slots.c.resource_id == resource_id,
                        slots.c.starts_at < ends_at,
                        slots.c.ends_at > starts_at,
                    )
                )
            )
        )

    def list(
        self, resource_id: UUID | None, available_only: bool, limit: int, offset: int
    ) -> list[Slot]:
        query = select(Slot)
        if resource_id:
            query = query.where(slots.c.resource_id == resource_id)
        if available_only:
            active = exists().where(
                reservations.c.slot_id == slots.c.id,
                reservations.c.status != ReservationStatus.CANCELLED,
            )
            query = query.where(slots.c.starts_at > self.clock.now(), ~active)
        return list(
            self.session.scalars(
                query.order_by(slots.c.starts_at, slots.c.id).limit(limit).offset(offset)
            )
        )
