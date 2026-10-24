from typing import Protocol
from uuid import UUID


class TokenCodec(Protocol):
    def issue(self, user_id: UUID) -> str: ...
    def decode(self, token: str) -> UUID: ...
