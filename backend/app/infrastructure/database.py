from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


def build_engine(url: str) -> Engine:
    engine = create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False, "timeout": 15}
        if url.startswith("sqlite")
        else {},
    )
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def sqlite_foreign_keys(connection: object, _: object) -> None:
            # DB-API connection is driver-specific.
            connection.execute("PRAGMA foreign_keys=ON")  # type: ignore[attr-defined]

    return engine


def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


class SqlUnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session

    def commit(self) -> None:
        self.session.commit()
