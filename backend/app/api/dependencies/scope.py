from collections.abc import Iterator
from typing import Annotated, cast

from fastapi import Depends, Request

from app.application.ports.service_provider import ServiceProvider
from app.application.service_scope import ServiceScope


def get_scope(request: Request) -> Iterator[ServiceScope]:
    provider = cast(ServiceProvider, request.app.state.services)
    with provider.scope() as services:
        yield services


Scope = Annotated[ServiceScope, Depends(get_scope)]
