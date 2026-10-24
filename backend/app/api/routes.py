from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import (
    CurrentUser,
    admin,
    auth_service,
    catalog_service,
    payment_service,
    reservation_service,
)
from app.api.schemas import (
    LoginInput,
    PaymentOutput,
    RegisterInput,
    ReservationInput,
    ReservationOutput,
    ResourceInput,
    ResourceOutput,
    SlotInput,
    SlotOutput,
    TokenOutput,
    TransactionOutput,
    UserOutput,
)
from app.application.auth import AuthService
from app.application.catalog import CatalogService
from app.application.payments import PaymentService
from app.application.reservations import ReservationService
from app.domain.entities import Payment, Reservation, Resource, Slot, Transaction, User
from app.infrastructure.security import issue_token

router = APIRouter(prefix="/api/v1")
Auth = Annotated[AuthService, Depends(auth_service)]
Catalog = Annotated[CatalogService, Depends(catalog_service)]
Bookings = Annotated[ReservationService, Depends(reservation_service)]
Payments = Annotated[PaymentService, Depends(payment_service)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]


@router.post("/auth/register", response_model=UserOutput, status_code=201, tags=["auth"])
def register(data: RegisterInput, service: Auth) -> User:
    return service.register(data.name, str(data.email), data.password)


@router.post("/auth/login", response_model=TokenOutput, tags=["auth"])
def login(data: LoginInput, service: Auth, request: Request) -> TokenOutput:
    user = service.authenticate(str(data.email), data.password)
    return TokenOutput(
        access_token=issue_token(user.id, request.app.state.settings),
        user=UserOutput.model_validate(user),
    )


@router.get("/auth/me", response_model=UserOutput, tags=["auth"])
def me(user: CurrentUser) -> User:
    return user


@router.get("/resources", response_model=list[ResourceOutput], tags=["catalog"])
def list_resources(service: Catalog, limit: Limit = 50, offset: Offset = 0) -> list[Resource]:
    return service.resources(limit, offset)


@router.post(
    "/resources",
    response_model=ResourceOutput,
    status_code=201,
    dependencies=[Depends(admin)],
    tags=["catalog"],
)
def create_resource(data: ResourceInput, service: Catalog) -> Resource:
    return service.create_resource(data.name, data.description)


@router.get("/slots", response_model=list[SlotOutput], tags=["catalog"])
def list_slots(
    service: Catalog,
    resource_id: UUID | None = None,
    available_only: bool = True,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[Slot]:
    return service.slots(resource_id, available_only, limit, offset)


@router.post(
    "/slots",
    response_model=SlotOutput,
    status_code=201,
    dependencies=[Depends(admin)],
    tags=["catalog"],
)
def create_slot(data: SlotInput, service: Catalog) -> Slot:
    return service.create_slot(data.resource_id, data.starts_at, data.ends_at, data.price_irr)


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


@router.post(
    "/reservations/{reservation_id}/payments", response_model=PaymentOutput, tags=["payments"]
)
def create_payment(reservation_id: UUID, user: CurrentUser, service: Payments) -> Payment:
    return service.create(user.id, reservation_id)


@router.post("/payments/{payment_id}/verify", response_model=TransactionOutput, tags=["payments"])
def verify_payment(payment_id: UUID, user: CurrentUser, service: Payments) -> Transaction:
    return service.verify(user.id, payment_id)


@router.get("/transactions", response_model=list[TransactionOutput], tags=["payments"])
def list_transactions(
    user: CurrentUser,
    service: Payments,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[Transaction]:
    return service.transactions(user.id, limit, offset)
