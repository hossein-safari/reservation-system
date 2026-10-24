from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies.identity import CurrentUser
from app.api.dependencies.services import Payments
from app.api.schemas.payment import PaymentOutput
from app.api.schemas.transaction import TransactionOutput
from app.domain.entities.payment import Payment
from app.domain.entities.transaction import Transaction

router = APIRouter()


@router.post(
    "/reservations/{reservation_id}/payments", response_model=PaymentOutput, tags=["payments"]
)
def create_payment(reservation_id: UUID, user: CurrentUser, service: Payments) -> Payment:
    return service.create(user.id, reservation_id)


@router.post("/payments/{payment_id}/verify", response_model=TransactionOutput, tags=["payments"])
def verify_payment(payment_id: UUID, user: CurrentUser, service: Payments) -> Transaction:
    return service.verify(user.id, payment_id)
