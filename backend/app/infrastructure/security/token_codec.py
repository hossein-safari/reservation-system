from datetime import timedelta
from uuid import UUID

import jwt

from app.application.ports.clock import Clock
from app.domain.errors.authentication import AuthenticationError


class JwtTokenCodec:
    def __init__(self, secret: str, lifetime_minutes: int, clock: Clock) -> None:
        self.secret = secret
        self.lifetime_minutes = lifetime_minutes
        self.clock = clock

    def issue(self, user_id: UUID) -> str:
        now = self.clock.now()
        return jwt.encode(
            {
                "sub": str(user_id),
                "iat": now,
                "exp": now + timedelta(minutes=self.lifetime_minutes),
            },
            self.secret,
            algorithm="HS256",
        )

    def decode(self, token: str) -> UUID:
        try:
            payload = jwt.decode(
                token, self.secret, algorithms=["HS256"], options={"require": ["sub", "iat", "exp"]}
            )
            return UUID(payload["sub"])
        except (jwt.InvalidTokenError, ValueError, TypeError, KeyError) as exc:
            raise AuthenticationError("invalid_token", "A valid access token is required.") from exc
