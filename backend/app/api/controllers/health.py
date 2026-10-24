from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.dependencies.health import Readiness

router = APIRouter()


@router.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", tags=["health"])
def ready(probe: Readiness) -> JSONResponse:
    if not probe.is_ready():
        return JSONResponse(status_code=503, content={"status": "not_ready"})
    return JSONResponse(content={"status": "ready"})
