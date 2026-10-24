from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.domain.entities.slot import Slot
from tests.integration.helpers import API, create_slot


def test_slot_rules_and_health(client: TestClient, admin_headers: dict[str, str]) -> None:
    slot = create_slot(client, admin_headers)
    data = {key: slot[key] for key in ("resource_id", "starts_at", "ends_at", "price_irr")}
    assert client.post(f"{API}/slots", headers=admin_headers, json=data).status_code == 409
    for changes in (
        {"price_irr": 0},
        {"price_irr": 1.5},
        {"price_irr": True},
        {"starts_at": "2030-01-01T10:00:00"},
        {"ends_at": data["starts_at"]},
    ):
        assert (
            client.post(f"{API}/slots", headers=admin_headers, json=data | changes).status_code
            == 422
        )
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 200


def test_past_slot_cannot_be_reserved(
    client: TestClient,
    admin_headers: dict[str, str],
    customer_headers: dict[str, str],
) -> None:
    slot = create_slot(client, admin_headers)
    with client.app.state.container.database.sessions() as session:
        from uuid import UUID

        entity = session.get(Slot, UUID(str(slot["id"])))
        entity.starts_at = datetime.now(UTC) - timedelta(hours=2)
        entity.ends_at = datetime.now(UTC) - timedelta(hours=1)
        session.commit()
    assert (
        client.post(
            f"{API}/reservations", headers=customer_headers, json={"slot_id": slot["id"]}
        ).status_code
        == 409
    )
