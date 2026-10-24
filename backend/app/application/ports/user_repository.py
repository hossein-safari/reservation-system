from typing import Protocol
from uuid import UUID

from app.domain.entities.user import User


class UserRepository(Protocol):
    def by_email(self, email: str) -> User | None: ...
    def by_id(self, user_id: UUID) -> User | None: ...
    def add(self, user: User) -> None: ...
