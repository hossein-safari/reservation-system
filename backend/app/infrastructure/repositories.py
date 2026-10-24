from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.domain.entities import (
    Payment,
    Reservation,
    ReservationStatus,
    Resource,
    Slot,
    Transaction,
    User,
    utcnow,
)
from app.infrastructure.models import payments, reservations, resources, slots, transactions, users


class SqlAuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(users.c.email == email))

    def by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def add(self, user: User) -> None:
        self.session.add(user)
        self.session.flush()


class SqlCatalogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def resources(self, limit: int, offset: int) -> list[Resource]:
        return list(
            self.session.scalars(
                select(Resource)
                .order_by(resources.c.name, resources.c.id)
                .limit(limit)
                .offset(offset)
            )
        )

    def resource(self, resource_id: UUID, *, lock: bool = False) -> Resource | None:
        query = select(Resource).where(resources.c.id == resource_id)
        return self.session.scalar(query.with_for_update() if lock else query)

    def add_resource(self, resource: Resource) -> None:
        self.session.add(resource)
        self.session.flush()

    def add_slot(self, slot: Slot) -> None:
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

    def slots(
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
            query = query.where(slots.c.starts_at > utcnow(), ~active)
        return list(
            self.session.scalars(
                query.order_by(slots.c.starts_at, slots.c.id).limit(limit).offset(offset)
            )
        )


class SqlBookingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def slot(self, slot_id: UUID) -> Slot | None:
        return self.session.get(Slot, slot_id)

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

    def owned(self, reservation_id: UUID, user_id: UUID) -> Reservation | None:
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

    def transaction(self, payment_id: UUID) -> Transaction | None:
        return self.session.scalar(
            select(Transaction).where(transactions.c.payment_id == payment_id)
        )

    def add_transaction(self, transaction: Transaction) -> None:
        self.session.add(transaction)
        self.session.flush()

    def list_transactions(self, user_id: UUID, limit: int, offset: int) -> list[Transaction]:
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
