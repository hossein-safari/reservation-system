from datetime import datetime
from uuid import UUID

from app.api.schemas.common import Output
from app.domain.entities.payment import PaymentStatus


class PaymentOutput(Output):
    id: UUID
    reservation_id: UUID
    amount_irr: int
    provider_reference: str
    status: PaymentStatus
    created_at: datetime
