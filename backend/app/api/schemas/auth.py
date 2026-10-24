from pydantic import BaseModel, EmailStr, Field

from app.api.schemas.common import Input
from app.api.schemas.user import UserOutput
from app.application.commands.register_user import RegisterUserCommand


# Keep the public schema name while sharing validation with CLI provisioning.
class RegisterInput(RegisterUserCommand):
    pass


class LoginInput(Input):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)


class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOutput
