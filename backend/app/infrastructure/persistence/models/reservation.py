from sqlalchemy import BigInteger, CheckConstraint, Column, ForeignKey, Index, Table, Uuid, text
from sqlalchemy.orm import relationship

from app.domain.entities.reservation import Reservation, ReservationStatus
from app.domain.entities.slot import Slot
from app.infrastructure.persistence.metadata import mapper_registry, metadata
from app.infrastructure.persistence.models.types import UTCDateTime, enum_type

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


def map_entity() -> None:
    mapper_registry.map_imperatively(
        Reservation,
        reservations,
        properties={"slot": relationship(Slot, lazy="selectin", viewonly=True)},
    )
