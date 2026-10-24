from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.payment import Payment
from app.infrastructure.persistence.models.payment import payments


class SqlPaymentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def for_reservation(self, reservation_id: UUID) -> Payment | None:
        return self.session.scalar(
            select(Payment)
            .where(
                payments.c.reservation_id == reservation_id,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def get(self, payment_id: UUID) -> Payment | None:
        return self.session.get(Payment, payment_id)

    def add(self, payment: Payment) -> None:
        self.session.add(payment)
        self.session.flush()
