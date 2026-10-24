"""Imperative mapping keeps domain entities independent of the ORM."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    MetaData,
    String,
    Table,
    Text,
    Uuid,
    text,
)
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import registry, relationship
from sqlalchemy.types import TypeDecorator

from app.domain.entities import (
    Payment,
    PaymentStatus,
    Reservation,
    ReservationStatus,
    Resource,
    Role,
    Slot,
    Transaction,
    User,
)


class UTCDateTime(TypeDecorator[datetime]):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("Naive datetime is not permitted")
            return value.astimezone(UTC)
        return None

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is not None:
            return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
        return None


metadata = MetaData()
mapper_registry = registry(metadata=metadata)


def enum_type(enum: Any, name: str) -> Enum:
    return Enum(
        enum,
        name=name,
        native_enum=False,
        create_constraint=True,
        values_callable=lambda values: [value.value for value in values],
    )


users = Table(
    "users",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("name", String(120), nullable=False),
    Column("email", String(254), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("role", enum_type(Role, "user_role"), nullable=False),
)
resources = Table(
    "resources",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("name", String(120), nullable=False),
    Column("description", Text, nullable=False),
)
slots = Table(
    "slots",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("resource_id", Uuid, ForeignKey("resources.id"), nullable=False, index=True),
    Column("starts_at", UTCDateTime, nullable=False),
    Column("ends_at", UTCDateTime, nullable=False),
    Column("price_irr", BigInteger, nullable=False),
    CheckConstraint("ends_at > starts_at", name="ck_slot_interval"),
    CheckConstraint("price_irr > 0", name="ck_slot_price"),
    Index("ix_slots_starts_at", "starts_at"),
)
reservations = Table(
    "reservations",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("user_id", Uuid, ForeignKey("users.id"), nullable=False, index=True),
    Column("slot_id", Uuid, ForeignKey("slots.id"), nullable=False),
    Column("amount_irr", BigInteger, nullable=False),
    Column("status", enum_type(ReservationStatus, "reservation_status"), nullable=False),
    Column("created_at", UTCDateTime, nullable=False),
    CheckConstraint("amount_irr > 0", name="ck_reservation_amount"),
    Index(
        "uq_active_reservation_slot",
        "slot_id",
        unique=True,
        sqlite_where=text("status IN ('pending', 'confirmed')"),
        postgresql_where=text("status IN ('pending', 'confirmed')"),
    ),
)
payments = Table(
    "payments",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("reservation_id", Uuid, ForeignKey("reservations.id"), nullable=False, unique=True),
    Column("amount_irr", BigInteger, nullable=False),
    Column("provider_reference", String(160), nullable=False, unique=True),
    Column("status", enum_type(PaymentStatus, "payment_status"), nullable=False),
    Column("created_at", UTCDateTime, nullable=False),
    CheckConstraint("amount_irr > 0", name="ck_payment_amount"),
)
transactions = Table(
    "transactions",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("payment_id", Uuid, ForeignKey("payments.id"), nullable=False, unique=True),
    Column("reference", String(160), nullable=False, unique=True),
    Column("amount_irr", BigInteger, nullable=False),
    Column("created_at", UTCDateTime, nullable=False),
    CheckConstraint("amount_irr > 0", name="ck_transaction_amount"),
)

for entity, table in (
    (User, users),
    (Resource, resources),
    (Slot, slots),
    (Reservation, reservations),
    (Payment, payments),
    (Transaction, transactions),
):
    mapper_registry.map_imperatively(
        entity,
        table,
        properties={"slot": relationship(Slot, lazy="selectin", viewonly=True)}
        if entity is Reservation
        else {},
    )
