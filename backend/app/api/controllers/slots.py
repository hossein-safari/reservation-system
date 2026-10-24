from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies.identity import admin
from app.api.dependencies.pagination import Limit, Offset
from app.api.dependencies.services import Slots
from app.api.schemas.slot import SlotInput, SlotOutput
from app.domain.entities.slot import Slot

router = APIRouter()


@router.get("/slots", response_model=list[SlotOutput], tags=["catalog"])
def list_slots(
    service: Slots,
    resource_id: UUID | None = None,
    available_only: bool = True,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[Slot]:
    return service.list(resource_id, available_only, limit, offset)


@router.post(
    "/slots",
    response_model=SlotOutput,
    status_code=201,
    dependencies=[Depends(admin)],
    tags=["catalog"],
)
def create_slot(data: SlotInput, service: Slots) -> Slot:
    return service.create(data.resource_id, data.starts_at, data.ends_at, data.price_irr)
