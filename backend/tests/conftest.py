import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.application.auth import AuthService
from app.config import Settings
from app.domain.entities import Role
from app.infrastructure.database import SqlUnitOfWork
from app.infrastructure.models import metadata
from app.infrastructure.repositories import SqlAuthRepository
from app.infrastructure.security import ArgonPasswordHasher
from app.main import create_app


@pytest.fixture
def client(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    url = os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    monkeypatch.setenv("DATABASE_URL", url)
    settings = Settings(database_url=url, app_env="test")
    app = create_app(settings)
    # Only TEST_DATABASE_URL is eligible for destructive test setup.
    with app.state.engine.begin() as connection:
        metadata.drop_all(connection)
        connection.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    from app.config import get_settings

    get_settings.cache_clear()
    command.upgrade(Config("alembic.ini"), "head")
    with app.state.sessions() as session:
        AuthService(
            SqlAuthRepository(session), ArgonPasswordHasher(), SqlUnitOfWork(session)
        ).register(
            "Administrator",
            "admin@example.com",
            "admin-password-123",
            role=Role.ADMIN,
        )
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin-password-123",
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def customer_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Customer",
            "email": "customer@example.com",
            "password": "customer-password-123",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "customer@example.com",
            "password": "customer-password-123",
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
