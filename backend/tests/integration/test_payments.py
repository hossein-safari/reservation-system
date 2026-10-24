import pytest
from fastapi.testclient import TestClient

from app.domain.errors.base import DomainError
from app.infrastructure.payments.development_gateway import DevelopmentGateway
from tests.integration.helpers import API, create_slot


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
