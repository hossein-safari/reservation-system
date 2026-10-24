from fastapi.testclient import TestClient

from tests.integration.helpers import API, create_slot


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
