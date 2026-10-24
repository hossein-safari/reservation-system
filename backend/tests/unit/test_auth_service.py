from uuid import uuid4

import pytest

from app.application.commands.register_user import RegisterUserCommand
from app.application.services.auth import AuthService
from app.domain.entities.user import Role
from app.domain.errors.authentication import AuthenticationError
from tests.fakes.password_hasher import FakePasswordHasher
from tests.fakes.token_codec import FakeTokenCodec
from tests.fakes.unit_of_work import MemoryUnitOfWork
from tests.fakes.users import MemoryUsers


def test_auth_uses_injected_token_and_hash_adapters() -> None:
    users, hasher, tokens, uow = (
        MemoryUsers(),
        FakePasswordHasher(),
        FakeTokenCodec(),
        MemoryUnitOfWork(),
    )
    service = AuthService(users, hasher, tokens, uow)
    user = service.register(
        RegisterUserCommand(name="Customer", email="User@example.com", password="test-password-123")
    )
    assert user.role == Role.CUSTOMER
    login = service.login("USER@example.com", "test-password-123")
    assert login.user is user
    assert service.current_user(login.access_token) is user
    assert uow.commits == 1


def test_unknown_account_uses_verifier_without_exposing_dummy_hash() -> None:
    hasher = FakePasswordHasher()
    service = AuthService(MemoryUsers(), hasher, FakeTokenCodec(), MemoryUnitOfWork())
    with pytest.raises(AuthenticationError):
        service.login("unknown@example.com", "test-password")
    assert hasher.verified_hashes == [None]
    with pytest.raises(AuthenticationError):
        service.current_user(FakeTokenCodec().issue(uuid4()))
