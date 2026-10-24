from uuid import UUID

from app.domain.errors.authentication import AuthenticationError


class FakeTokenCodec:
    def issue(self, user_id: UUID) -> str:
        return f"test-only-{user_id}"

    def decode(self, token: str) -> UUID:
        try:
            return UUID(token.removeprefix("test-only-"))
        except ValueError as exc:
            raise AuthenticationError("invalid_token", "Invalid test token.") from exc
