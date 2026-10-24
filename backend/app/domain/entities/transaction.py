from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.time import utcnow
from app.domain.validation import validate_amount


@dataclass(eq=False)
class Transaction:
    payment_id: UUID
    reference: str
    amount_irr: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        validate_amount(self.amount_irr)
