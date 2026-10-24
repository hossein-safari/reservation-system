from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies.identity import CurrentUser
from app.api.dependencies.pagination import Limit, Offset
from app.api.dependencies.services import Bookings
from app.api.schemas.reservation import ReservationInput, ReservationOutput
from app.domain.entities.reservation import Reservation

router = APIRouter()


@router.get("/reservations", response_model=list[ReservationOutput], tags=["reservations"])
def list_reservations(
    user: CurrentUser,
    service: Bookings,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[Reservation]:
    return service.list_owned(user.id, limit, offset)


@router.post(
    "/reservations", response_model=ReservationOutput, status_code=201, tags=["reservations"]
)
def create_reservation(data: ReservationInput, user: CurrentUser, service: Bookings) -> Reservation:
    return service.create(user.id, data.slot_id)


@router.post(
    "/reservations/{reservation_id}/cancel", response_model=ReservationOutput, tags=["reservations"]
)
def cancel_reservation(reservation_id: UUID, user: CurrentUser, service: Bookings) -> Reservation:
    return service.cancel(user.id, reservation_id)
