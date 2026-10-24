from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.auth import AuthService
from app.application.catalog import CatalogService
from app.application.payments import PaymentService
from app.application.reservations import ReservationService
from app.domain.entities import Role, User
from app.domain.errors import DomainError
from app.infrastructure.database import SqlUnitOfWork
from app.infrastructure.gateway import DevelopmentGateway
from app.infrastructure.repositories import (
    SqlAuthRepository,
    SqlBookingRepository,
    SqlCatalogRepository,
    SqlPaymentRepository,
)
from app.infrastructure.security import ArgonPasswordHasher, decode_token

bearer = HTTPBearer(auto_error=False)
hasher = ArgonPasswordHasher()


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.sessions() as session:
        try:
            yield session
        except IntegrityError as exc:
            session.rollback()
            raise DomainError(
                "conflict", "The record conflicts with an existing operation."
            ) from exc
        finally:
            session.rollback()


DatabaseSession = Annotated[Session, Depends(get_session)]


def current_user(
    request: Request,
    session: DatabaseSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None:
        raise DomainError("authentication_required", "Authentication is required.", 401)
    user_id = decode_token(credentials.credentials, request.app.state.settings)
    user = SqlAuthRepository(session).by_id(user_id)
    if user is None:
        raise DomainError("invalid_token", "A valid access token is required.", 401)
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def admin(user: CurrentUser) -> User:
    if user.role != Role.ADMIN:
        raise DomainError("forbidden", "Administrator access is required.", 403)
    return user


def auth_service(session: DatabaseSession) -> AuthService:
    return AuthService(SqlAuthRepository(session), hasher, SqlUnitOfWork(session))


def catalog_service(session: DatabaseSession) -> CatalogService:
    return CatalogService(SqlCatalogRepository(session), SqlUnitOfWork(session))


def reservation_service(session: DatabaseSession) -> ReservationService:
    return ReservationService(SqlBookingRepository(session), SqlUnitOfWork(session))


def payment_service(request: Request, session: DatabaseSession) -> PaymentService:
    return PaymentService(
        SqlBookingRepository(session),
        SqlPaymentRepository(session),
        DevelopmentGateway(request.app.state.settings.app_env),
        SqlUnitOfWork(session),
    )
