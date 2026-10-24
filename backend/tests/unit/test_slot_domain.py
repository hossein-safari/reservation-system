from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.entities.slot import Slot
from app.domain.errors.validation import ValidationError


@pytest.mark.parametrize("amount", [0, -1, 1_000_000_000_001, True, 1.5])
def test_invalid_amount_is_rejected_outside_http(amount: int) -> None:
    start = datetime(2035, 1, 2, tzinfo=UTC)
    with pytest.raises(ValidationError):
        Slot(uuid4(), start, start + timedelta(hours=1), amount)


def test_naive_time_is_rejected_outside_http() -> None:
    start = datetime(2035, 1, 2)
    with pytest.raises(ValidationError, match="Timezone-aware"):
        Slot(uuid4(), start, start + timedelta(hours=1), 1000)
