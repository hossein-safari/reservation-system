from typing import Annotated, cast

from fastapi import Depends, Request

from app.application.ports.readiness_probe import ReadinessProbe


def readiness_probe(request: Request) -> ReadinessProbe:
    return cast(ReadinessProbe, request.app.state.readiness)


Readiness = Annotated[ReadinessProbe, Depends(readiness_probe)]
