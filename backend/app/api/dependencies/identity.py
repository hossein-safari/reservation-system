from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies.scope import Scope
from app.domain.entities.user import User
from app.domain.errors.authentication import AuthenticationError

bearer = HTTPBearer(auto_error=False)


def current_user(
    services: Scope,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None:
        raise AuthenticationError("authentication_required", "Authentication is required.")
    return services.auth.current_user(credentials.credentials)


CurrentUser = Annotated[User, Depends(current_user)]


def admin(user: CurrentUser) -> User:
    user.require_admin()
    return user
