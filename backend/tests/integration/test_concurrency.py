from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.infrastructure.persistence.models.reservation import reservations
from app.infrastructure.persistence.models.slot import slots
from app.infrastructure.persistence.models.transaction import transactions
from tests.integration.helpers import API, create_slot


def test_concurrent_reservations_have_one_winner(
    client: TestClient,
    admin_headers: dict[str, str],
    customer_headers: dict[str, str],
) -> None:
    if client.app.state.container.database.engine.dialect.name != "postgresql":
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
    with client.app.state.container.database.sessions() as session:
        assert session.scalar(select(func.count()).select_from(reservations)) == 1


def test_concurrent_verification_records_one_transaction(
    client: TestClient,
    admin_headers: dict[str, str],
    customer_headers: dict[str, str],
) -> None:
    if client.app.state.container.database.engine.dialect.name != "postgresql":
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
    with client.app.state.container.database.sessions() as session:
        assert session.scalar(select(func.count()).select_from(transactions)) == 1


def test_database_rejects_overlapping_slots(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    if client.app.state.container.database.engine.dialect.name != "postgresql":
        pytest.skip("Exclusion constraint is PostgreSQL-specific")
    from uuid import UUID, uuid4

    from sqlalchemy.exc import IntegrityError

    slot = create_slot(client, admin_headers)
    with client.app.state.container.database.sessions() as session, pytest.raises(IntegrityError):
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
