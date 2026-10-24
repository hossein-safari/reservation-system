from datetime import timedelta
from uuid import uuid4

import pytest

from app.config import Settings
from app.domain.errors.authentication import AuthenticationError
from app.domain.errors.unavailable import UnavailableError
from app.domain.time import utcnow
from app.infrastructure.payments.development_gateway import DevelopmentGateway
from app.infrastructure.security.password_hasher import ArgonPasswordHasher
from app.infrastructure.security.token_codec import JwtTokenCodec
from tests.fakes.clock import FrozenClock


def test_production_disables_simulator_and_requires_secret() -> None:
    with pytest.raises(ValueError, match="APP_SECRET_KEY"):
        Settings(app_env="production")
    with pytest.raises(UnavailableError):
        DevelopmentGateway("production").create(uuid4(), 1000)


def test_password_adapter_verifies_known_and_unknown_accounts() -> None:
    hasher = ArgonPasswordHasher()
    hashed = hasher.hash("test-password")
    assert hasher.verify("test-password", hashed)
    assert not hasher.verify("wrong-password", hashed)
    assert not hasher.verify("test-password", None)


def test_token_adapter_rejects_expired_and_invalid_tokens() -> None:
    clock = FrozenClock(utcnow() - timedelta(hours=1))
    codec = JwtTokenCodec("test-secret-that-is-long-enough-123456", 1, clock)
    with pytest.raises(AuthenticationError):
        codec.decode(codec.issue(uuid4()))
    with pytest.raises(AuthenticationError):
        codec.decode("not-a-token")
