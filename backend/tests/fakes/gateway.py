from uuid import UUID

from app.domain.errors.conflict import ConflictError


class FakeGateway:
    def __init__(self) -> None:
        self.calls = 0
        self.fail = False

    def create(self, reservation_id: UUID, amount_irr: int) -> str:
        return f"fake-{reservation_id}"

    def verify(self, provider_reference: str, amount_irr: int) -> str:
        self.calls += 1
        if self.fail:
            raise ConflictError("verification_failed", "Verification failed.")
        return f"receipt-{provider_reference}"
