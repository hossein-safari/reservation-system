from fastapi import APIRouter

from app.api.dependencies.identity import CurrentUser
from app.api.dependencies.pagination import Limit, Offset
from app.api.dependencies.services import Transactions
from app.api.schemas.transaction import TransactionOutput
from app.domain.entities.transaction import Transaction

router = APIRouter()


@router.get("/transactions", response_model=list[TransactionOutput], tags=["payments"])
def list_transactions(
    user: CurrentUser,
    service: Transactions,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[Transaction]:
    return service.list_owned(user.id, limit, offset)
