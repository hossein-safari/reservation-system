from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.infrastructure.persistence.models.user import users


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(users.c.email == email))

    def by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def add(self, user: User) -> None:
        self.session.add(user)
        self.session.flush()
