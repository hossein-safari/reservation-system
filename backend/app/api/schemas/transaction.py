from datetime import datetime
from uuid import UUID

from app.api.schemas.common import Output


class TransactionOutput(Output):
    id: UUID
    payment_id: UUID
    reference: str
    amount_irr: int
    created_at: datetime
