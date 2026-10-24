from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.errors.authorization import AuthorizationError
from app.domain.validation import validate_name


class Role(StrEnum):
    CUSTOMER = "customer"
    ADMIN = "admin"


@dataclass(eq=False)
class User:
    name: str
    email: str
    password_hash: str
    role: Role = Role.CUSTOMER
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = validate_name(self.name)
        self.email = self.email.strip().lower()

    def require_admin(self) -> None:
        if self.role != Role.ADMIN:
            raise AuthorizationError("forbidden", "Administrator access is required.")
