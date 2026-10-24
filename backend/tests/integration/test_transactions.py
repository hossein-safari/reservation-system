from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from app.domain.entities.resource import Resource
from app.domain.errors.conflict import ConflictError
from app.domain.errors.unavailable import UnavailableError
from app.infrastructure.persistence.models.resource import resources
from app.infrastructure.persistence.repositories.resource import SqlResourceRepository
from app.infrastructure.persistence.unit_of_work import SqlUnitOfWork


def test_unit_of_work_rolls_back_without_http(client: TestClient) -> None:
    database = client.app.state.container.database
    with database.session() as session:
        repository = SqlResourceRepository(session)
        with pytest.raises(RuntimeError, match="after flush"), SqlUnitOfWork(session).transaction():
            repository.add(Resource("Must roll back"))
            raise RuntimeError("after flush")
    with database.session() as session:
        assert session.scalar(select(func.count()).select_from(resources)) == 0


def test_failed_commit_rolls_back_flushed_data(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = client.app.state.container.database
    with database.session() as session:

        def fail_commit() -> None:
            raise RuntimeError("commit failed")

        monkeypatch.setattr(session, "commit", fail_commit)
        with (
            pytest.raises(RuntimeError, match="commit failed"),
            SqlUnitOfWork(session).transaction(),
        ):
            SqlResourceRepository(session).add(Resource("Must not persist"))
    with database.session() as session:
        assert session.scalar(select(func.count()).select_from(resources)) == 0


def test_integrity_failure_translates_and_cleans_session(client: TestClient) -> None:
    database = client.app.state.container.database
    resource = Resource("Unique primary key", id=uuid4())
    with database.session() as session, SqlUnitOfWork(session).transaction():
        SqlResourceRepository(session).add(resource)
    with database.session() as session:
        with pytest.raises(ConflictError), SqlUnitOfWork(session).transaction():
            SqlResourceRepository(session).add(Resource("Duplicate", id=resource.id))
        # The same session is usable after the rollback.
        with SqlUnitOfWork(session).transaction():
            SqlResourceRepository(session).add(Resource("After rollback"))
    with database.session() as session:
        assert session.scalar(select(func.count()).select_from(resources)) == 2


def test_query_failure_is_translated_outside_http(client: TestClient) -> None:
    with pytest.raises(UnavailableError) as failure, client.app.state.container.database.session():
        raise OperationalError("query", {}, RuntimeError("driver unavailable"))
    assert failure.value.code == "database_unavailable"
