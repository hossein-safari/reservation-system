from datetime import datetime
from uuid import UUID

from pydantic import AwareDatetime

from app.api.schemas.common import Amount, Input, Output


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
