from datetime import timedelta
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.config import Settings
from app.domain.entities import utcnow
from app.domain.errors import DomainError


class ArgonPasswordHasher:
    def __init__(self) -> None:
        self.password_hash = PasswordHash.recommended()
        self.dummy_hash = self.password_hash.hash("dummy-password-for-timing")

    def hash(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        return self.password_hash.verify(password, hashed)


def issue_token(user_id: UUID, settings: Settings) -> str:
    now = utcnow()
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_minutes),
        },
        settings.app_secret_key,
        algorithm="HS256",
    )


def decode_token(token: str, settings: Settings) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.app_secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "iat", "exp"]},
        )
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError) as exc:
        raise DomainError("invalid_token", "A valid access token is required.", 401) from exc
