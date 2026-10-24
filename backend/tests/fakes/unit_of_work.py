from collections.abc import Iterator
from contextlib import contextmanager


class MemoryUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            yield
        except BaseException:
            self.rollbacks += 1
            raise
        else:
            self.commits += 1
