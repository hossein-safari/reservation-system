from app.application.ports.resource_repository import ResourceRepository
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.resource import Resource


class ResourceService:
    def __init__(self, resources: ResourceRepository, uow: UnitOfWork) -> None:
        self._resources = resources
        self._uow = uow

    def list(self, limit: int, offset: int) -> list[Resource]:
        return self._resources.list(limit, offset)

    def create(self, name: str, description: str) -> Resource:
        with self._uow.transaction():
            resource = Resource(name, description)
            self._resources.add(resource)
        return resource
