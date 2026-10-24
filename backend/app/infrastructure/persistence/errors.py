from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.domain.errors.base import DomainError
from app.domain.errors.conflict import ConflictError
from app.domain.errors.unavailable import UnavailableError


def translate_database_error(error: SQLAlchemyError) -> DomainError:
    if isinstance(error, IntegrityError):
        return ConflictError("conflict", "The record conflicts with an existing operation.")
    return UnavailableError("database_unavailable", "The database is temporarily unavailable.")
