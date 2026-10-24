from uuid import UUID

from app.domain.entities.resource import Resource


class MemoryResources:
    def __init__(self) -> None:
        self.records: dict[UUID, Resource] = {}
        self.locked: list[UUID] = []

    def get_for_update(self, resource_id: UUID) -> Resource | None:
        self.locked.append(resource_id)
        return self.records.get(resource_id)

    def add(self, resource: Resource) -> None:
        self.records[resource.id] = resource

    def list(self, limit: int, offset: int) -> list[Resource]:
        return sorted(self.records.values(), key=lambda resource: (resource.name, resource.id))[
            offset : offset + limit
        ]
