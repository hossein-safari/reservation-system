import argparse
from getpass import getpass

from app.api.schemas import RegisterInput
from app.application.auth import AuthService
from app.config import get_settings
from app.domain.entities import Role
from app.domain.errors import DomainError
from app.infrastructure.database import SqlUnitOfWork, build_engine, session_factory
from app.infrastructure.repositories import SqlAuthRepository
from app.infrastructure.security import ArgonPasswordHasher


def main() -> None:
    parser = argparse.ArgumentParser(description="Reservation administration")
    parser.add_argument("command", choices=["create-admin"])
    parser.parse_args()
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    password = getpass("Password (12+ characters): ")
    if password != getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")
    data = RegisterInput(name=name, email=email, password=password)
    engine = build_engine(get_settings().database_url)
    try:
        with session_factory(engine)() as session:
            service = AuthService(
                SqlAuthRepository(session), ArgonPasswordHasher(), SqlUnitOfWork(session)
            )
            user = service.register(data.name, str(data.email), data.password, role=Role.ADMIN)
            print(f"Administrator created: {user.email}")
    except DomainError as exc:
        raise SystemExit(exc.message) from exc
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
