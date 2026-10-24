from fastapi import APIRouter, Depends

from app.api.dependencies.identity import admin
from app.api.dependencies.pagination import Limit, Offset
from app.api.dependencies.services import Resources
from app.api.schemas.resource import ResourceInput, ResourceOutput
from app.domain.entities.resource import Resource

router = APIRouter()


@router.get("/resources", response_model=list[ResourceOutput], tags=["catalog"])
def list_resources(service: Resources, limit: Limit = 50, offset: Offset = 0) -> list[Resource]:
    return service.list(limit, offset)


@router.post(
    "/resources",
    response_model=ResourceOutput,
    status_code=201,
    dependencies=[Depends(admin)],
    tags=["catalog"],
)
def create_resource(data: ResourceInput, service: Resources) -> Resource:
    return service.create(data.name, data.description)
