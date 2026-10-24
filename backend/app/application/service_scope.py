from dataclasses import dataclass

from app.application.services.auth import AuthService
from app.application.services.payments import PaymentService
from app.application.services.reservations import ReservationService
from app.application.services.resources import ResourceService
from app.application.services.slots import SlotService
from app.application.services.transactions import TransactionService


@dataclass(frozen=True)
class ServiceScope:
    auth: AuthService
    resources: ResourceService
    slots: SlotService
    reservations: ReservationService
    payments: PaymentService
    transactions: TransactionService
