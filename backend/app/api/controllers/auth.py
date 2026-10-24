from fastapi import APIRouter

from app.api.dependencies.identity import CurrentUser
from app.api.dependencies.services import Auth
from app.api.schemas.auth import LoginInput, RegisterInput, TokenOutput
from app.api.schemas.user import UserOutput
from app.domain.entities.user import User

router = APIRouter()


@router.post("/auth/register", response_model=UserOutput, status_code=201, tags=["auth"])
def register(data: RegisterInput, service: Auth) -> User:
    return service.register(data)


@router.post("/auth/login", response_model=TokenOutput, tags=["auth"])
def login(data: LoginInput, service: Auth) -> TokenOutput:
    session = service.login(str(data.email), data.password)
    return TokenOutput(
        access_token=session.access_token, user=UserOutput.model_validate(session.user)
    )


@router.get("/auth/me", response_model=UserOutput, tags=["auth"])
def me(user: CurrentUser) -> User:
    return user
