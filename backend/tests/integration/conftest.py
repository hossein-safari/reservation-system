import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.application.commands.register_user import RegisterUserCommand
from app.config import Settings, get_settings
from app.infrastructure.persistence.metadata import metadata
from app.main import create_app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    url = os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    monkeypatch.setenv("DATABASE_URL", url)
    app = create_app(Settings(database_url=url, app_env="test"))
    database = app.state.container.database
    # Only the explicitly selected, dedicated test database is eligible for reset.
    with database.engine.begin() as connection:
        metadata.drop_all(connection)
        connection.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    get_settings.cache_clear()
    command.upgrade(Config("alembic.ini"), "head")
    with app.state.container.scope() as services:
        services.auth.create_admin(
            RegisterUserCommand(
                name="Administrator",
                email="admin@example.com",
                password="admin-password-123",
            )
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
