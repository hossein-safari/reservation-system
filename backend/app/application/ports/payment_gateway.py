from typing import Protocol
from uuid import UUID


class PaymentGateway(Protocol):
    def create(self, reservation_id: UUID, amount_irr: int) -> str: ...
    def verify(self, provider_reference: str, amount_irr: int) -> str: ...
