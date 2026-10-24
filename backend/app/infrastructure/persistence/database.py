from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.persistence.engine import build_engine
from app.infrastructure.persistence.errors import translate_database_error


class Database:
    def __init__(self, url: str) -> None:
        self.engine = build_engine(url)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)
        config_path = Path(__file__).resolve().parents[3] / "alembic.ini"
        self.migration_head = ScriptDirectory.from_config(
            Config(str(config_path))
        ).get_current_head()

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self.sessions() as session:
            try:
                yield session
            except SQLAlchemyError as exc:
                session.rollback()
                raise translate_database_error(exc) from exc
            finally:
                session.rollback()

    def is_ready(self) -> bool:
        try:
            with self.engine.connect() as connection:
                current = connection.scalar(text("SELECT version_num FROM alembic_version"))
            return current is not None and current == self.migration_head
        except SQLAlchemyError:
            return False

    def close(self) -> None:
        self.engine.dispose()
