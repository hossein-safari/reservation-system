from uuid import UUID

from app.domain.entities.user import User
from app.domain.errors.conflict import ConflictError


class MemoryUsers:
    def __init__(self) -> None:
        self.records: dict[UUID, User] = {}

    def by_email(self, email: str) -> User | None:
        return next((user for user in self.records.values() if user.email == email), None)

    def by_id(self, user_id: UUID) -> User | None:
        return self.records.get(user_id)

    def add(self, user: User) -> None:
        if self.by_email(user.email):
            raise ConflictError("conflict", "Email must be unique.")
        self.records[user.id] = user
