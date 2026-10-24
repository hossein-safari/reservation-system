from fastapi.testclient import TestClient

from tests.integration.helpers import API


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
