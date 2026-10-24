"""Register each aggregate's mapping once at the application boundary."""

from app.infrastructure.persistence.models import (
    payment,
    reservation,
    resource,
    slot,
    transaction,
    user,
)

_configured = False


def configure_mappings() -> None:
    global _configured
    if _configured:
        return
    user.map_entity()
    resource.map_entity()
    slot.map_entity()
    reservation.map_entity()
    payment.map_entity()
    transaction.map_entity()
    _configured = True
