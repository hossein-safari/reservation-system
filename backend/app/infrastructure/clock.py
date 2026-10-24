from datetime import datetime

from app.domain.time import utcnow


class SystemClock:
    def now(self) -> datetime:
        return utcnow()
