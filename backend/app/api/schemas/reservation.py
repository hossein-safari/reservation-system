from datetime import datetime
from uuid import UUID

from app.api.schemas.common import Input, Output
from app.api.schemas.slot import SlotOutput
from app.domain.entities.reservation import ReservationStatus


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
