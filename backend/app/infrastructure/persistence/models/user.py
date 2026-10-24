from sqlalchemy import Column, String, Table, Uuid

from app.domain.entities.user import Role, User
from app.infrastructure.persistence.metadata import mapper_registry, metadata
from app.infrastructure.persistence.models.types import enum_type

users = Table(
    "users",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("name", String(120), nullable=False),
    Column("email", String(254), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("role", enum_type(Role, "user_role"), nullable=False),
)


def map_entity() -> None:
    mapper_registry.map_imperatively(User, users)
