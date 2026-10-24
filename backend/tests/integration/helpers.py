from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

API = "/api/v1"


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
