from sqlalchemy import BigInteger, CheckConstraint, Column, ForeignKey, Index, Table, Uuid

from app.domain.entities.slot import Slot
from app.infrastructure.persistence.metadata import mapper_registry, metadata
from app.infrastructure.persistence.models.types import UTCDateTime

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


def map_entity() -> None:
    mapper_registry.map_imperatively(Slot, slots)
