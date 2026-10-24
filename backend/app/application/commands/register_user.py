from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints


class RegisterUserCommand(BaseModel):
    """Validated input shared by HTTP registration and administrator provisioning."""

    model_config = ConfigDict(extra="forbid")
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=12, max_length=128)
