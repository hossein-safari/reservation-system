from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.domain.entities import Slot
from app.domain.errors import DomainError
from app.infrastructure.gateway import DevelopmentGateway
from app.infrastructure.models import reservations, slots, transactions

API = "/api/v1"


def test_gateway_failure_preserves_pending_reservation(
    client: TestClient,
    admin_headers: dict[str, str],
    customer_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slot = create_slot(client, admin_headers)
    reservation = client.post(
        f"{API}/reservations", headers=customer_headers, json={"slot_id": slot["id"]}
    ).json()
    payment = client.post(
        f"{API}/reservations/{reservation['id']}/payments", headers=customer_headers
    ).json()

    def fail(self: DevelopmentGateway, provider_reference: str, amount_irr: int) -> str:
        raise DomainError("verification_failed", "Verification failed")

    monkeypatch.setattr(DevelopmentGateway, "verify", fail)
    assert (
        client.post(f"{API}/payments/{payment['id']}/verify", headers=customer_headers).status_code
        == 409
    )
    assert (
        client.get(f"{API}/reservations", headers=customer_headers).json()[0]["status"] == "pending"
    )
    assert client.get(f"{API}/transactions", headers=customer_headers).json() == []


def create_slot(client: TestClient, headers: dict[str, str]) -> dict[str, object]:
    resource = client.post(f"{API}/resources", headers=headers, json={"name": "Court A"}).json()
    start = datetime.now(UTC) + timedelta(days=2)
    response = client.post(
        f"{API}/slots",
        headers=headers,
        json={
            "resource_id": resource["id"],
            "starts_at": start.isoformat(),
            "ends_at": (start + timedelta(hours=1)).isoformat(),
            "price_irr": 250000,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_auth_roles_and_input_validation(
    client: TestClient, customer_headers: dict[str, str]
) -> None:
    assert client.get(f"{API}/auth/me").status_code == 401
    response = client.get(f"{API}/auth/me", headers=customer_headers)
    assert response.json()["role"] == "customer"
    assert "password_hash" not in response.json()
    assert (
        client.post(
            f"{API}/resources", headers=customer_headers, json={"name": "Hidden"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"{API}/auth/register",
            json={
                "name": "Intruder",
                "email": "a@example.com",
                "password": "long-password",
                "role": "admin",
            },
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"{API}/auth/login",
            json={
                "email": "customer@example.com",
                "password": "wrong-password",
            },
        ).status_code
        == 401
    )
    assert (
        client.post(
            f"{API}/auth/register",
            json={
                "name": "Duplicate",
                "email": "CUSTOMER@example.com",
                "password": "long-password",
            },
        ).status_code
        == 409
    )
    assert client.get(f"{API}/resources?limit=101").status_code == 422


def test_full_booking_payment_flow(
    client: TestClient,
    admin_headers: dict[str, str],
    customer_headers: dict[str, str],
) -> None:
    slot = create_slot(client, admin_headers)
    response = client.post(
        f"{API}/reservations", headers=customer_headers, json={"slot_id": slot["id"]}
    )
    assert response.status_code == 201
    reservation = response.json()
    assert reservation["amount_irr"] == 250000
    assert reservation["slot"]["resource_id"] == slot["resource_id"]
    assert (
        client.post(
            f"{API}/reservations", headers=admin_headers, json={"slot_id": slot["id"]}
        ).status_code
        == 409
    )
    assert client.get(f"{API}/slots").json() == []
    assert len(client.get(f"{API}/slots?available_only=false").json()) == 1
    payment_url = f"{API}/reservations/{reservation['id']}/payments"
    assert client.post(payment_url, headers=admin_headers).status_code == 404
    payment = client.post(payment_url, headers=customer_headers).json()
    assert payment == client.post(payment_url, headers=customer_headers).json()
    verify_url = f"{API}/payments/{payment['id']}/verify"
    assert client.post(verify_url, headers=admin_headers).status_code == 404
    receipt = client.post(verify_url, headers=customer_headers)
    assert receipt.status_code == 200
    assert receipt.json() == client.post(verify_url, headers=customer_headers).json()
    assert (
        client.get(f"{API}/reservations", headers=customer_headers).json()[0]["status"]
        == "confirmed"
    )
    assert len(client.get(f"{API}/transactions", headers=customer_headers).json()) == 1
    assert client.get(f"{API}/transactions", headers=admin_headers).json() == []
    assert (
        client.post(
            f"{API}/reservations/{reservation['id']}/cancel", headers=customer_headers
        ).status_code
        == 409
    )


def test_cancel_releases_slot_and_blocks_existing_payment(
    client: TestClient,
    admin_headers: dict[str, str],
    customer_headers: dict[str, str],
) -> None:
    slot = create_slot(client, admin_headers)
    reservation = client.post(
        f"{API}/reservations", headers=customer_headers, json={"slot_id": slot["id"]}
    ).json()
    payment = client.post(
        f"{API}/reservations/{reservation['id']}/payments", headers=customer_headers
    ).json()
    cancel_url = f"{API}/reservations/{reservation['id']}/cancel"
    assert client.post(cancel_url, headers=admin_headers).status_code == 404
    assert client.post(cancel_url, headers=customer_headers).json()["status"] == "cancelled"
    assert (
        client.post(f"{API}/payments/{payment['id']}/verify", headers=customer_headers).status_code
        == 409
    )
    assert (
        client.post(
            f"{API}/reservations", headers=admin_headers, json={"slot_id": slot["id"]}
        ).status_code
        == 201
    )


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
    with client.app.state.sessions() as session:
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


def test_concurrent_reservations_have_one_winner(
    client: TestClient,
    admin_headers: dict[str, str],
    customer_headers: dict[str, str],
) -> None:
    if client.app.state.engine.dialect.name != "postgresql":
        pytest.skip("Row concurrency is verified on PostgreSQL")
    slot = create_slot(client, admin_headers)

    def reserve(_: int) -> int:
        return client.post(
            f"{API}/reservations", headers=customer_headers, json={"slot_id": slot["id"]}
        ).status_code

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(reserve, range(4)))
    assert results.count(201) == 1
    assert results.count(409) == 3
    with client.app.state.sessions() as session:
        assert session.scalar(select(func.count()).select_from(reservations)) == 1


def test_concurrent_verification_records_one_transaction(
    client: TestClient,
    admin_headers: dict[str, str],
    customer_headers: dict[str, str],
) -> None:
    if client.app.state.engine.dialect.name != "postgresql":
        pytest.skip("Row locks are verified on PostgreSQL")
    slot = create_slot(client, admin_headers)
    reservation = client.post(
        f"{API}/reservations", headers=customer_headers, json={"slot_id": slot["id"]}
    ).json()
    payment = client.post(
        f"{API}/reservations/{reservation['id']}/payments", headers=customer_headers
    ).json()

    def verify(_: int) -> str:
        response = client.post(f"{API}/payments/{payment['id']}/verify", headers=customer_headers)
        assert response.status_code == 200
        return response.json()["id"]

    with ThreadPoolExecutor(max_workers=4) as executor:
        receipts = list(executor.map(verify, range(4)))
    assert len(set(receipts)) == 1
    with client.app.state.sessions() as session:
        assert session.scalar(select(func.count()).select_from(transactions)) == 1


def test_database_rejects_overlapping_slots(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    if client.app.state.engine.dialect.name != "postgresql":
        pytest.skip("Exclusion constraint is PostgreSQL-specific")
    from uuid import UUID, uuid4

    from sqlalchemy.exc import IntegrityError

    slot = create_slot(client, admin_headers)
    with client.app.state.sessions() as session, pytest.raises(IntegrityError):
        session.execute(
            slots.insert().values(
                id=uuid4(),
                resource_id=UUID(str(slot["resource_id"])),
                starts_at=datetime.fromisoformat(str(slot["starts_at"])),
                ends_at=datetime.fromisoformat(str(slot["ends_at"])),
                price_irr=100,
            )
        )
        session.commit()
