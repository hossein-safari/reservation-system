from uuid import UUID

from pydantic import Field

from app.api.schemas.common import Input, Name, Output


class ResourceInput(Input):
    name: Name
    description: str = Field(default="", max_length=2000)


class ResourceOutput(Output):
    id: UUID
    name: str
    description: str
