from pwdlib import PasswordHash

from app.domain.errors.authentication import AuthenticationError


class ArgonPasswordHasher:
    def __init__(self) -> None:
        self.password_hash = PasswordHash.recommended()
        self._dummy_hash = self.password_hash.hash("dummy-password-for-timing")

    def hash(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify(self, password: str, hashed: str | None) -> bool:
        try:
            valid = self.password_hash.verify(password, hashed or self._dummy_hash)
        except (ValueError, TypeError) as exc:
            raise AuthenticationError("invalid_credentials", "Invalid email or password.") from exc
        return hashed is not None and valid
