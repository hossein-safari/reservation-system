from sqlalchemy import Column, String, Table, Text, Uuid

from app.domain.entities.resource import Resource
from app.infrastructure.persistence.metadata import mapper_registry, metadata

resources = Table(
    "resources",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("name", String(120), nullable=False),
    Column("description", Text, nullable=False),
)


def map_entity() -> None:
    mapper_registry.map_imperatively(Resource, resources)
