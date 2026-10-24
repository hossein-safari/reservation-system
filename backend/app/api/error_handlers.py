from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.errors.authentication import AuthenticationError
from app.domain.errors.authorization import AuthorizationError
from app.domain.errors.base import DomainError
from app.domain.errors.not_found import NotFoundError
from app.domain.errors.unavailable import UnavailableError
from app.domain.errors.validation import ValidationError

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    AuthenticationError: 401,
    AuthorizationError: 403,
    NotFoundError: 404,
    ValidationError: 422,
    UnavailableError: 503,
}


async def domain_error_handler(_: Request, exception: Exception) -> JSONResponse:
    error = cast(DomainError, exception)
    status = next((code for kind, code in STATUS_BY_ERROR.items() if isinstance(error, kind)), 409)
    return JSONResponse(
        status_code=status,
        content={"error": {"code": error.code, "message": error.message}},
        headers={"WWW-Authenticate": "Bearer"} if status == 401 else None,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
