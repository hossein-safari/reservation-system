from typing import Annotated

from fastapi import Depends

from app.api.dependencies.scope import Scope
from app.application.services.auth import AuthService
from app.application.services.payments import PaymentService
from app.application.services.reservations import ReservationService
from app.application.services.resources import ResourceService
from app.application.services.slots import SlotService
from app.application.services.transactions import TransactionService


def auth_service(services: Scope) -> AuthService:
    return services.auth


def resource_service(services: Scope) -> ResourceService:
    return services.resources


def slot_service(services: Scope) -> SlotService:
    return services.slots


def reservation_service(services: Scope) -> ReservationService:
    return services.reservations


def payment_service(services: Scope) -> PaymentService:
    return services.payments


def transaction_service(services: Scope) -> TransactionService:
    return services.transactions


Auth = Annotated[AuthService, Depends(auth_service)]
Resources = Annotated[ResourceService, Depends(resource_service)]
Slots = Annotated[SlotService, Depends(slot_service)]
Bookings = Annotated[ReservationService, Depends(reservation_service)]
Payments = Annotated[PaymentService, Depends(payment_service)]
Transactions = Annotated[TransactionService, Depends(transaction_service)]
