from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.entities.slot import Slot
from tests.fakes.clock import FrozenClock


@pytest.fixture
def clock() -> FrozenClock:
    return FrozenClock(datetime(2035, 1, 1, 10, tzinfo=UTC))


@pytest.fixture
def slot(clock: FrozenClock) -> Slot:
    from datetime import timedelta

    return Slot(
        uuid4(), clock.now() + timedelta(days=1), clock.now() + timedelta(days=1, hours=1), 850000
    )
