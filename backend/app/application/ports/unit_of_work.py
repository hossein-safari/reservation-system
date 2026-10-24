from contextlib import AbstractContextManager
from typing import Protocol


class UnitOfWork(Protocol):
    def transaction(self) -> AbstractContextManager[None]: ...
