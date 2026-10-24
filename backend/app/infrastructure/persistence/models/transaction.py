from sqlalchemy import BigInteger, CheckConstraint, Column, ForeignKey, String, Table, Uuid

from app.domain.entities.transaction import Transaction
from app.infrastructure.persistence.metadata import mapper_registry, metadata
from app.infrastructure.persistence.models.types import UTCDateTime

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


def map_entity() -> None:
    mapper_registry.map_imperatively(Transaction, transactions)
