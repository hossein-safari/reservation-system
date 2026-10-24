from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.resource import Resource
from app.infrastructure.persistence.models.resource import resources


class SqlResourceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, limit: int, offset: int) -> list[Resource]:
        return list(
            self.session.scalars(
                select(Resource)
                .order_by(resources.c.name, resources.c.id)
                .limit(limit)
                .offset(offset)
            )
        )

    def add(self, resource: Resource) -> None:
        self.session.add(resource)
        self.session.flush()

    def get_for_update(self, resource_id: UUID) -> Resource | None:
        return self.session.scalar(
            select(Resource).where(resources.c.id == resource_id).with_for_update()
        )
