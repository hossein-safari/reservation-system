import argparse
from getpass import getpass

from pydantic import ValidationError

from app.application.commands.register_user import RegisterUserCommand
from app.bootstrap.container import ApplicationContainer
from app.config import get_settings
from app.domain.errors.base import DomainError


def main() -> None:
    parser = argparse.ArgumentParser(description="Reservation administration")
    parser.add_argument("command", choices=["create-admin"])
    parser.parse_args()
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    password = getpass("Password (12+ characters): ")
    if password != getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")
    try:
        command = RegisterUserCommand(name=name, email=email, password=password)
    except ValidationError:
        # ValidationError includes input values; never print a password from its repr.
        raise SystemExit("Enter a valid name, email and a password of 12-128 characters.") from None
    container = ApplicationContainer(get_settings())
    try:
        with container.scope() as services:
            user = services.auth.create_admin(command)
            print(f"Administrator created: {user.email}")
    except DomainError as exc:
        raise SystemExit(exc.message) from exc
    finally:
        container.close()


if __name__ == "__main__":
    main()
