from typing import Protocol


class ReadinessProbe(Protocol):
    def is_ready(self) -> bool: ...
