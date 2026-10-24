from uuid import UUID

from app.domain.errors import DomainError


class DevelopmentGateway:
    """Deterministic local simulator. Never connect this to a bank callback."""

    def __init__(self, environment: str) -> None:
        self.enabled = environment in {"development", "test"}

    def _check_enabled(self) -> None:
        if not self.enabled:
            raise DomainError("gateway_unavailable", "A production gateway is not configured.", 503)

    def create(self, reservation_id: UUID, amount_irr: int) -> str:
        self._check_enabled()
        return f"dev-{reservation_id}"

    def verify(self, provider_reference: str, amount_irr: int) -> str:
        self._check_enabled()
        if not provider_reference.startswith("dev-") or amount_irr <= 0:
            raise DomainError("verification_failed", "The payment could not be verified.")
        return f"receipt-{provider_reference}"
