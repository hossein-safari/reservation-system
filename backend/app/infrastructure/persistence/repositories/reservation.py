from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.domain.entities.reservation import Reservation, ReservationStatus
from app.infrastructure.persistence.models.reservation import reservations


class SqlReservationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def active_for_slot(self, slot_id: UUID) -> bool:
        return bool(
            self.session.scalar(
                select(
                    exists().where(
                        reservations.c.slot_id == slot_id,
                        reservations.c.status != ReservationStatus.CANCELLED,
                    )
                )
            )
        )

    def add(self, reservation: Reservation) -> None:
        self.session.add(reservation)
        self.session.flush()

    def owned_for_update(self, reservation_id: UUID, user_id: UUID) -> Reservation | None:
        return self.session.scalar(
            select(Reservation)
            .where(
                reservations.c.id == reservation_id,
                reservations.c.user_id == user_id,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Reservation]:
        return list(
            self.session.scalars(
                select(Reservation)
                .where(reservations.c.user_id == user_id)
                .order_by(reservations.c.created_at.desc(), reservations.c.id)
                .limit(limit)
                .offset(offset)
            )
        )
