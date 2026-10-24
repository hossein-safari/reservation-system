from dataclasses import dataclass

from app.domain.entities.user import User


@dataclass(frozen=True)
class AuthenticatedSession:
    user: User
    access_token: str
