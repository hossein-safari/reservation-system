from typing import Protocol
from uuid import UUID

from app.domain.entities.transaction import Transaction


class TransactionRepository(Protocol):
    def for_payment(self, payment_id: UUID) -> Transaction | None: ...
    def add(self, transaction: Transaction) -> None: ...
    def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Transaction]: ...
