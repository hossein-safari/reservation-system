from contextlib import AbstractContextManager
from typing import Protocol

from app.application.service_scope import ServiceScope


class ServiceProvider(Protocol):
    def scope(self) -> AbstractContextManager[ServiceScope]: ...
