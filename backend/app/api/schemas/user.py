from uuid import UUID

from app.api.schemas.common import Output
from app.domain.entities.user import Role


class UserOutput(Output):
    id: UUID
    name: str
    email: str
    role: Role
