from typing import Protocol
from uuid import UUID

from app.domain.entities.resource import Resource


class ResourceRepository(Protocol):
    def list(self, limit: int, offset: int) -> list[Resource]: ...
    def get_for_update(self, resource_id: UUID) -> Resource | None: ...
    def add(self, resource: Resource) -> None: ...
