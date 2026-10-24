from uuid import UUID

from app.application.ports.transaction_repository import TransactionRepository
from app.domain.entities.transaction import Transaction


class TransactionService:
    def __init__(self, transactions: TransactionRepository) -> None:
        self._transactions = transactions

    def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Transaction]:
        return self._transactions.list_owned(user_id, limit, offset)
