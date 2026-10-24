from typing import Protocol
from uuid import UUID

from app.domain.entities.payment import Payment


class PaymentRepository(Protocol):
    def for_reservation(self, reservation_id: UUID) -> Payment | None: ...
    def get(self, payment_id: UUID) -> Payment | None: ...
    def add(self, payment: Payment) -> None: ...
