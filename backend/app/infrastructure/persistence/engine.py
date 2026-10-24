from sqlite3 import Connection

from sqlalchemy import Engine, create_engine, event


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
        def sqlite_foreign_keys(connection: Connection, _: object) -> None:
            connection.execute("PRAGMA foreign_keys=ON")

    return engine
