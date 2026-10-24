from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.infrastructure.persistence.errors import translate_database_error


class SqlUnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Complete the active session transaction, including any preceding reads."""
        try:
            yield
            self.session.commit()
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise translate_database_error(exc) from exc
        except BaseException:
            self.session.rollback()
            raise
