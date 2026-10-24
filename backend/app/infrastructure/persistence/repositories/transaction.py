from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.payment import Payment
from app.domain.entities.reservation import Reservation
from app.domain.entities.transaction import Transaction
from app.infrastructure.persistence.models.payment import payments
from app.infrastructure.persistence.models.reservation import reservations
from app.infrastructure.persistence.models.transaction import transactions


class SqlTransactionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def for_payment(self, payment_id: UUID) -> Transaction | None:
        return self.session.scalar(
            select(Transaction).where(transactions.c.payment_id == payment_id)
        )

    def add(self, transaction: Transaction) -> None:
        self.session.add(transaction)
        self.session.flush()

    def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Transaction]:
        query = (
            select(Transaction)
            .join(Payment, transactions.c.payment_id == payments.c.id)
            .join(Reservation, payments.c.reservation_id == reservations.c.id)
            .where(reservations.c.user_id == user_id)
            .order_by(transactions.c.created_at.desc(), transactions.c.id)
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(query))
