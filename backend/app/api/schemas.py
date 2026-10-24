from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.domain.entities import PaymentStatus, ReservationStatus, Role

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Amount = Annotated[int, Field(gt=0, le=1_000_000_000_000, strict=True)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Output(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterInput(Input):
    name: Name
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=12, max_length=128)


class LoginInput(Input):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)


class UserOutput(Output):
    id: UUID
    name: str
    email: str
    role: Role


class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOutput


class ResourceInput(Input):
    name: Name
    description: str = Field(default="", max_length=2000)


class ResourceOutput(Output):
    id: UUID
    name: str
    description: str


class SlotInput(Input):
    resource_id: UUID
    starts_at: AwareDatetime
    ends_at: AwareDatetime
    price_irr: Amount


class SlotOutput(Output):
    id: UUID
    resource_id: UUID
    starts_at: datetime
    ends_at: datetime
    price_irr: int


class ReservationInput(Input):
    slot_id: UUID


class ReservationOutput(Output):
    id: UUID
    user_id: UUID
    slot_id: UUID
    amount_irr: int
    status: ReservationStatus
    created_at: datetime
    slot: SlotOutput


class PaymentOutput(Output):
    id: UUID
    reservation_id: UUID
    amount_irr: int
    provider_reference: str
    status: PaymentStatus
    created_at: datetime


class TransactionOutput(Output):
    id: UUID
    payment_id: UUID
    reference: str
    amount_irr: int
    created_at: datetime
