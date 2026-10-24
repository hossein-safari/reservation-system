from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import router
from app.config import Settings, get_settings
from app.domain.errors import DomainError
from app.infrastructure.database import build_engine, session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    engine = build_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        engine.dispose()

    app = FastAPI(title="Reservation API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessions = session_factory(engine)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(DomainError)
    async def domain_error(_: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"error": {"code": error.code, "message": error.message}},
            headers={"WWW-Authenticate": "Bearer"} if error.status_code == 401 else None,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(_: Request, error: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "database_unavailable",
                    "message": "The database is temporarily unavailable.",
                }
            },
        )

    @app.get("/health/live", tags=["health"])
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    def ready() -> JSONResponse:
        try:
            with engine.connect() as connection:
                version = connection.scalar(text("SELECT version_num FROM alembic_version"))
            if version != "0001_initial":
                raise ValueError("Migration is not current")
        except (SQLAlchemyError, ValueError):
            return JSONResponse(status_code=503, content={"status": "not_ready"})
        return JSONResponse(content={"status": "ready"})

    app.include_router(router)
    return app


app = create_app()
