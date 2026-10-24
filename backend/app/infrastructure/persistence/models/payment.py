from sqlalchemy import BigInteger, CheckConstraint, Column, ForeignKey, String, Table, Uuid

from app.domain.entities.payment import Payment, PaymentStatus
from app.infrastructure.persistence.metadata import mapper_registry, metadata
from app.infrastructure.persistence.models.types import UTCDateTime, enum_type

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


def map_entity() -> None:
    mapper_registry.map_imperatively(Payment, payments)
