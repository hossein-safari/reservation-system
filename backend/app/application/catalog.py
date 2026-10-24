from datetime import UTC, datetime
from uuid import UUID

from app.application.ports import CatalogRepository, UnitOfWork
from app.domain.entities import Resource, Slot
from app.domain.errors import DomainError, not_found
from app.domain.rules import validate_slot


class CatalogService:
    def __init__(self, catalog: CatalogRepository, uow: UnitOfWork) -> None:
        self.catalog = catalog
        self.uow = uow

    def resources(self, limit: int, offset: int) -> list[Resource]:
        return self.catalog.resources(limit, offset)

    def create_resource(self, name: str, description: str) -> Resource:
        resource = Resource(name.strip(), description.strip())
        self.catalog.add_resource(resource)
        self.uow.commit()
        return resource

    def slots(
        self, resource_id: UUID | None, available_only: bool, limit: int, offset: int
    ) -> list[Slot]:
        return self.catalog.slots(resource_id, available_only, limit, offset)

    def create_slot(
        self, resource_id: UUID, starts_at: datetime, ends_at: datetime, price_irr: int
    ) -> Slot:
        validate_slot(starts_at, ends_at, price_irr)
        if not self.catalog.resource(resource_id, lock=True):
            raise not_found()
        if self.catalog.overlaps(resource_id, starts_at, ends_at):
            raise DomainError("overlapping_slot", "Slots for a resource cannot overlap.")
        slot = Slot(resource_id, starts_at.astimezone(UTC), ends_at.astimezone(UTC), price_irr)
        self.catalog.add_slot(slot)
        self.uow.commit()
        return slot
