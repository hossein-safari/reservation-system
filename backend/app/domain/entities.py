from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


def utcnow() -> datetime:
    return datetime.now(UTC)


class Role(StrEnum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class ReservationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"


@dataclass(eq=False)
class User:
    name: str
    email: str
    password_hash: str
    role: Role = Role.CUSTOMER
    id: UUID = field(default_factory=uuid4)


@dataclass(eq=False)
class Resource:
    name: str
    description: str = ""
    id: UUID = field(default_factory=uuid4)


@dataclass(eq=False)
class Slot:
    resource_id: UUID
    starts_at: datetime
    ends_at: datetime
    price_irr: int
    id: UUID = field(default_factory=uuid4)


@dataclass(eq=False)
class Reservation:
    user_id: UUID
    slot_id: UUID
    amount_irr: int
    status: ReservationStatus = ReservationStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utcnow)
    slot: Slot | None = field(default=None, init=False, repr=False)


@dataclass(eq=False)
class Payment:
    reservation_id: UUID
    amount_irr: int
    provider_reference: str
    status: PaymentStatus = PaymentStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utcnow)


@dataclass(eq=False)
class Transaction:
    payment_id: UUID
    reference: str
    amount_irr: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utcnow)
